"use client";

import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getCategories, getTransactions, updateTransaction } from "@/services/finance";
import type { Category, Transaction } from "@/types/api";

export default function TransactionsPage() {
  const [rows, setRows] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [tx, cats] = await Promise.all([getTransactions(query), getCategories()]);
      setRows(tx);
      setCategories(cats);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudieron cargar movimientos");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const categoryOptions = useMemo(() => categories.map((c) => ({ value: String(c.id), label: c.name })), [categories]);

  async function patch(id: number, payload: { category_id?: number; expense_type?: string }) {
    await updateTransaction(id, payload);
    await load();
  }

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Movimientos</h2>
        <p className="page-subtitle">Busca, filtra y reclasifica consumos importados desde resumenes.</p>
      </div>
      <Card>
        <CardContent className="p-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-end">
            <div className="flex-1 space-y-2">
              <Label>Busqueda</Label>
              <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Comercio o descripcion" />
            </div>
            <Button onClick={() => void load()}>Buscar</Button>
          </div>
        </CardContent>
      </Card>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {loading ? <p className="text-sm text-slate-500">Cargando movimientos...</p> : null}
      {!loading && !rows.length ? <EmptyState title="Sin movimientos" description="Subi un PDF o registra gastos manuales para empezar." /> : null}

      {rows.length ? (
        <Card>
          <CardContent className="overflow-x-auto p-0">
            <table className="w-full min-w-[980px] text-left text-sm">
              <thead className="border-b bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">Fecha</th>
                  <th className="px-4 py-3">Descripcion</th>
                  <th className="px-4 py-3">Categoria</th>
                  <th className="px-4 py-3">Tipo</th>
                  <th className="px-4 py-3">Banco</th>
                  <th className="px-4 py-3">Tarjeta</th>
                  <th className="px-4 py-3 text-right">Importe</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rows.map((row) => (
                  <tr key={row.id}>
                    <td className="px-4 py-3 text-slate-500">{formatDate(row.transaction_date)}</td>
                    <td className="px-4 py-3 font-medium text-slate-950">{row.normalized_description}</td>
                    <td className="px-4 py-3">
                      <select
                        className="h-9 rounded-md border border-input bg-white px-2 text-sm"
                        value={row.category?.id ?? ""}
                        onChange={(event) => void patch(row.id, { category_id: Number(event.target.value) })}
                      >
                        <option value="">Sin categoria</option>
                        {categoryOptions.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        className="h-9 rounded-md border border-input bg-white px-2 text-sm"
                        value={row.expense_type}
                        onChange={(event) => void patch(row.id, { expense_type: event.target.value })}
                      >
                        <option value="fixed">Fijo</option>
                        <option value="variable">Variable</option>
                        <option value="exceptional">Excepcional</option>
                      </select>
                    </td>
                    <td className="px-4 py-3 text-slate-500">{row.bank_name ?? "-"}</td>
                    <td className="px-4 py-3 text-slate-500">{row.card_type ?? row.card_brand ?? "-"}</td>
                    <td className="px-4 py-3 text-right font-medium">{formatCurrency(row.amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
