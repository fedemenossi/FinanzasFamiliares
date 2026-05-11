"use client";

import { useEffect, useState } from "react";
import { FileUp } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getUploadedFiles, uploadPdf } from "@/services/finance";
import type { Transaction, UploadedFile, UploadResult } from "@/types/api";

export default function UploadsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [rows, setRows] = useState<Transaction[]>([]);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [history, setHistory] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadHistory() {
    try {
      setHistory(await getUploadedFiles());
    } catch {
      setHistory([]);
    }
  }

  useEffect(() => {
    void loadHistory();
  }, []);

  async function submit() {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const uploadResult = await uploadPdf(file);
      setResult(uploadResult);
      setRows(uploadResult.transactions);
      await loadHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo procesar el PDF");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Subida de PDFs</h2>
        <p className="page-subtitle">Carga resumenes bancarios argentinos para extraer y clasificar movimientos.</p>
      </div>

      <Card>
        <CardContent className="p-6">
          <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-white px-6 py-12 text-center transition-colors hover:border-teal-500">
            <FileUp className="h-10 w-10 text-teal-700" />
            <span className="mt-4 text-sm font-semibold text-slate-950">{file ? file.name : "Arrastra o selecciona un PDF"}</span>
            <span className="mt-1 text-sm text-slate-500">Visa, Mastercard, AMEX o resumen bancario compatible</span>
            <input className="hidden" type="file" accept="application/pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          </label>
          <div className="mt-4 flex items-center gap-3">
            <Button onClick={submit} disabled={!file || loading}>
              {loading ? "Procesando..." : "Procesar PDF"}
            </Button>
            {error ? <p className="text-sm text-red-600">{error}</p> : null}
          </div>
        </CardContent>
      </Card>

      {result ? (
        <div className="grid gap-4 md:grid-cols-4">
          <ResultCard title="Parser" value={result.parser_name} />
          <ResultCard title="Banco" value={result.bank_name || "No reconocido"} />
          <ResultCard title="Extraidos" value={String(result.extracted_count)} />
          <ResultCard title="Nuevos / duplicados" value={`${result.created_count} / ${result.duplicate_count}`} />
          <ResultCard title="Texto extraido" value={`${result.raw_text_chars} caracteres`} />
          <div className="md:col-span-4 rounded-lg border border-teal-200 bg-teal-50 px-4 py-3 text-sm text-teal-800">{result.message}</div>
        </div>
      ) : null}

      {result?.ai_analysis ? <AIAnalysisCard analysis={result.ai_analysis} /> : null}

      {result && result.extracted_count === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Diagnostico del parser</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="mb-2 text-sm font-medium text-slate-900">Lineas candidatas con fecha e importe</p>
              {result.candidate_lines.length ? (
                <DebugLines lines={result.candidate_lines} />
              ) : (
                <p className="text-sm text-slate-500">No se encontraron lineas con fecha e importe. Si el texto extraido es 0, probablemente el PDF sea imagen y requiere OCR.</p>
              )}
            </div>
            <div>
              <p className="mb-2 text-sm font-medium text-slate-900">Primeras lineas extraidas</p>
              {result.diagnostic_lines.length ? <DebugLines lines={result.diagnostic_lines} /> : <p className="text-sm text-slate-500">No se pudo extraer texto del PDF.</p>}
            </div>
          </CardContent>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Movimientos nuevos {rows.length ? `(${rows.length})` : ""}</CardTitle>
        </CardHeader>
        <CardContent>
          {rows.length ? (
            <TransactionsMiniTable rows={rows} />
          ) : (
            <EmptyState
              title="Sin movimientos nuevos"
              description={
                result
                  ? "El PDF pudo haber tenido 0 movimientos detectados o todos los movimientos ya estaban importados. Revisa el resumen de procesamiento arriba."
                  : "Los movimientos nuevos apareceran aca despues de subir un PDF."
              }
            />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Historial de PDFs</CardTitle>
        </CardHeader>
        <CardContent>
          {history.length ? <UploadsHistory rows={history} /> : <EmptyState title="Sin PDFs cargados" description="Aca se mostraran los ultimos archivos procesados." />}
        </CardContent>
      </Card>
    </div>
  );
}

function AIAnalysisCard({ analysis }: { analysis: NonNullable<UploadResult["ai_analysis"]> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Analisis IA</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="flex flex-wrap gap-2 text-sm">
          <span className="rounded-md bg-slate-100 px-2 py-1 text-slate-700">Estado: {analysis.status}</span>
          {analysis.model ? <span className="rounded-md bg-slate-100 px-2 py-1 text-slate-700">Modelo: {analysis.model}</span> : null}
        </div>
        {analysis.status === "completed" ? (
          <>
            {analysis.summary ? <p className="text-sm leading-6 text-slate-700">{analysis.summary}</p> : null}
            <AIList title="Insights" rows={(analysis.insights || []).map((item) => `${item.title}: ${item.detail}`)} />
            <AIList
              title="Sugerencias de clasificacion"
              rows={(analysis.category_suggestions || []).map(
                (item) => `${item.description} -> ${item.suggested_category} (${item.expense_type}, ${(item.confidence * 100).toFixed(0)}%): ${item.reason}`
              )}
            />
            <AIList title="Anomalias" rows={(analysis.anomalies || []).map((item) => `${item.description} (${formatCurrency(item.amount)}): ${item.reason}`)} />
          </>
        ) : (
          <p className="text-sm text-slate-500">{analysis.error_message || "El analisis IA no se ejecuto para este PDF."}</p>
        )}
      </CardContent>
    </Card>
  );
}

function AIList({ title, rows }: { title: string; rows: string[] }) {
  if (!rows.length) return null;
  return (
    <div>
      <p className="mb-2 text-sm font-medium text-slate-950">{title}</p>
      <ul className="space-y-2">
        {rows.map((row) => (
          <li key={row} className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm leading-6 text-slate-600">
            {row}
          </li>
        ))}
      </ul>
    </div>
  );
}

function DebugLines({ lines }: { lines: string[] }) {
  return (
    <pre className="max-h-72 overflow-auto rounded-md border border-slate-200 bg-slate-950 p-4 text-xs leading-5 text-slate-100">
      {lines.map((line, index) => `${index + 1}. ${line}`).join("\n")}
    </pre>
  );
}

function ResultCard({ title, value }: { title: string; value: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-xs font-medium uppercase text-slate-500">{title}</p>
        <p className="mt-2 truncate text-sm font-semibold text-slate-950">{value}</p>
      </CardContent>
    </Card>
  );
}

function TransactionsMiniTable({ rows }: { rows: Transaction[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-b text-xs uppercase text-slate-500">
          <tr>
            <th className="py-3">Fecha</th>
            <th>Descripcion</th>
            <th>Categoria</th>
            <th className="text-right">Importe</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row) => (
            <tr key={row.id}>
              <td className="py-3 text-slate-500">{formatDate(row.transaction_date)}</td>
              <td className="font-medium text-slate-900">{row.normalized_description}</td>
              <td className="text-slate-500">{row.category?.name ?? "Sin categoria"}</td>
              <td className="text-right font-medium">{formatCurrency(row.amount)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function UploadsHistory({ rows }: { rows: UploadedFile[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-b text-xs uppercase text-slate-500">
          <tr>
            <th className="py-3">Fecha</th>
            <th>Archivo</th>
            <th>Banco</th>
            <th>Tipo</th>
            <th>Estado</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row) => (
            <tr key={row.id}>
              <td className="py-3 text-slate-500">{formatDate(row.created_at)}</td>
              <td className="font-medium text-slate-900">{row.original_filename}</td>
              <td className="text-slate-500">{row.bank_name ?? "-"}</td>
              <td className="text-slate-500">{row.statement_type ?? "-"}</td>
              <td className="text-slate-500">{row.status}</td>
              <td className="max-w-sm truncate text-red-600">{row.error_message ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
