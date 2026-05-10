"use client";

import { useState } from "react";
import { FileUp } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency, formatDate } from "@/lib/utils";
import { uploadPdf } from "@/services/finance";
import type { Transaction } from "@/types/api";

export default function UploadsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [rows, setRows] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      setRows(await uploadPdf(file));
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

      <Card>
        <CardHeader>
          <CardTitle>Movimientos extraidos {rows.length ? `(${rows.length})` : ""}</CardTitle>
        </CardHeader>
        <CardContent>
          {rows.length ? <TransactionsMiniTable rows={rows} /> : <EmptyState title="Sin procesamiento reciente" description="Los movimientos extraidos apareceran aca despues de subir un PDF." />}
        </CardContent>
      </Card>
    </div>
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
