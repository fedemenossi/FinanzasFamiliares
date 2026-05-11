import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import PdfAIAnalysis, StatementSummary, Transaction, UploadedFile, User
from app.ai.classifier import AIClassifier
from app.parsers.base_parser import normalize_description
from app.parsers.parser_factory import ParserFactory
from app.schemas import TransactionOut, UploadedFileOut, UploadResult
from app.services.bootstrap import get_category_by_name
from app.services.classifier import classify

router = APIRouter(prefix="/files", tags=["files"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadResult)
async def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    stored_name = f"{current_user.id}_{uuid4().hex}.pdf"
    stored_path = settings.upload_path / stored_name
    contents = await file.read()
    stored_path.write_bytes(contents)
    logger.info(
        "pdf_upload_started user_id=%s filename=%s bytes=%s stored_path=%s",
        current_user.id,
        file.filename,
        len(contents),
        stored_path,
    )

    uploaded = UploadedFile(
        user_id=current_user.id,
        original_filename=file.filename,
        stored_path=str(stored_path),
        status="processing",
    )
    db.add(uploaded)
    db.commit()
    db.refresh(uploaded)

    try:
        parser = ParserFactory.for_file(stored_path)
        logger.info("pdf_parser_detected uploaded_file_id=%s parser=%s", uploaded.id, parser.__class__.__name__)
        statement = parser.parse(stored_path)
        logger.info(
            "pdf_parsed uploaded_file_id=%s bank=%s card_type=%s extracted_count=%s text_chars=%s",
            uploaded.id,
            statement.bank_name,
            statement.card_type,
            len(statement.transactions),
            len(statement.raw_text or ""),
        )
        uploaded.bank_name = statement.bank_name
        uploaded.statement_type = statement.card_type or statement.card_brand
        uploaded.status = "processed"
        db.add(
            StatementSummary(
                user_id=current_user.id,
                uploaded_file_id=uploaded.id,
                bank_name=statement.bank_name,
                card_brand=statement.card_brand,
                card_type=statement.card_type,
                previous_balance=statement.previous_balance,
                current_balance=statement.current_balance,
                minimum_payment=statement.minimum_payment,
            )
        )

        created: list[Transaction] = []
        classified_for_ai: list[dict] = []
        duplicate_count = 0
        for parsed in statement.transactions:
            normalized = normalize_description(parsed.raw_description)
            classification = classify(normalized, parsed.is_installment)
            classified_for_ai.append(
                {
                    "date": parsed.transaction_date.date().isoformat(),
                    "description": normalized,
                    "amount": float(parsed.amount),
                    "currency": parsed.currency,
                    "is_installment": parsed.is_installment,
                    "installment_current": parsed.installment_current,
                    "installment_total": parsed.installment_total,
                    "rule_category": classification.category_name,
                    "rule_expense_type": classification.expense_type,
                }
            )
            duplicate = db.scalar(
                select(Transaction.id).where(
                    Transaction.user_id == current_user.id,
                    Transaction.transaction_date == parsed.transaction_date,
                    Transaction.normalized_description == normalized,
                    Transaction.amount == parsed.amount,
                    Transaction.bank_name == statement.bank_name,
                    Transaction.card_type == statement.card_type,
                )
            )
            if duplicate:
                duplicate_count += 1
                continue

            category = get_category_by_name(db, current_user.id, classification.category_name)
            transaction = Transaction(
                user_id=current_user.id,
                uploaded_file_id=uploaded.id,
                bank_name=statement.bank_name,
                card_brand=statement.card_brand,
                card_type=statement.card_type,
                card_last_digits=parsed.card_last_digits,
                cardholder_name=parsed.cardholder_name,
                transaction_date=parsed.transaction_date,
                voucher_number=parsed.voucher_number,
                raw_description=parsed.raw_description,
                normalized_description=normalized,
                amount=parsed.amount,
                currency=parsed.currency,
                is_installment=parsed.is_installment,
                installment_current=parsed.installment_current,
                installment_total=parsed.installment_total,
                category_id=category.id,
                expense_type=classification.expense_type,
            )
            db.add(transaction)
            created.append(transaction)

        db.commit()
        for transaction in created:
            db.refresh(transaction)
        created_with_categories = db.scalars(
            select(Transaction)
            .options(joinedload(Transaction.category))
            .where(Transaction.id.in_([transaction.id for transaction in created]))
            .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        ).all() if created else []

        ai_analysis = run_ai_analysis(db, current_user.id, uploaded.id, statement, classified_for_ai)
        logger.info(
            "pdf_upload_completed uploaded_file_id=%s extracted_count=%s created_count=%s duplicate_count=%s",
            uploaded.id,
            len(statement.transactions),
            len(created),
            duplicate_count,
        )
        message = (
            f"PDF procesado. Extraidos: {len(statement.transactions)}. Nuevos: {len(created)}. Duplicados: {duplicate_count}."
        )
        if not statement.transactions:
            message = "PDF procesado, pero no se detectaron movimientos con los patrones actuales del parser."
        elif statement.transactions and not created:
            message = "PDF procesado. Todos los movimientos detectados ya estaban importados."
        return UploadResult(
            uploaded_file=uploaded,
            parser_name=parser.__class__.__name__,
            bank_name=statement.bank_name,
            statement_type=statement.card_type or statement.card_brand,
            extracted_count=len(statement.transactions),
            created_count=len(created),
            duplicate_count=duplicate_count,
            raw_text_chars=len(statement.raw_text or ""),
            diagnostic_lines=statement.diagnostic_lines,
            candidate_lines=statement.candidate_lines,
            transactions=created_with_categories,
            ai_analysis=ai_analysis,
            message=message,
        )
    except Exception as exc:
        uploaded.status = "error"
        uploaded.error_message = str(exc)
        db.commit()
        logger.exception("pdf_upload_failed uploaded_file_id=%s filename=%s", uploaded.id, file.filename)
        raise HTTPException(status_code=422, detail=f"No se pudo procesar el PDF: {exc}") from exc


@router.get("", response_model=list[UploadedFileOut])
def list_uploaded_files(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(
        select(UploadedFile)
        .where(UploadedFile.user_id == current_user.id)
        .order_by(UploadedFile.created_at.desc())
        .limit(50)
    ).all()


def run_ai_analysis(
    db: Session,
    user_id: int,
    uploaded_file_id: int,
    statement,
    classified_for_ai: list[dict],
) -> PdfAIAnalysis | None:
    analysis = PdfAIAnalysis(
        user_id=user_id,
        uploaded_file_id=uploaded_file_id,
        model=get_settings().openai_model,
        status="skipped",
        error_message=None,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    ai = AIClassifier()
    if not ai.enabled:
        analysis.status = "skipped"
        analysis.error_message = "OPENAI_API_KEY no configurada"
        db.commit()
        db.refresh(analysis)
        return analysis

    if not classified_for_ai:
        analysis.status = "skipped"
        analysis.error_message = "No hay movimientos extraidos para analizar"
        db.commit()
        db.refresh(analysis)
        return analysis

    try:
        result = ai.analyze_statement(statement, classified_for_ai)
        if not result:
            analysis.status = "skipped"
            analysis.error_message = "OpenAI no devolvio resultado"
        else:
            analysis.status = "completed"
            analysis.summary = result.get("summary")
            analysis.insights = result.get("insights", [])
            analysis.category_suggestions = result.get("category_suggestions", [])
            analysis.anomalies = result.get("anomalies", [])
            analysis.raw_response = result
        db.commit()
        db.refresh(analysis)
        return analysis
    except Exception as exc:
        logger.exception("openai_analysis_failed uploaded_file_id=%s", uploaded_file_id)
        analysis.status = "error"
        analysis.error_message = str(exc)
        db.commit()
        db.refresh(analysis)
        return analysis
