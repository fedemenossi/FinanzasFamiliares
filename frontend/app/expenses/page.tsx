"use client";

import { useEffect, useState } from "react";

import { ManualEntryForm } from "@/components/forms/manual-entry-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getCategories, getExpenses } from "@/services/finance";
import type { Category, ManualExpense } from "@/types/api";

export default function ExpensesPage() {
  const [rows, setRows] = useState<ManualExpense[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  async function load() {
    const [expenses, cats] = await Promise.all([getExpenses(), getCategories()]);
    setRows(expenses);
    setCategories(cats);
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Gastos manuales</h2>
        <p className="page-subtitle">Carga gastos que no aparecen en resumenes bancarios.</p>
      </div>
      <ManualEntryForm mode="expense" categories={categories} onCreated={() => void load()} />
      <Card>
        <CardHeader>
          <CardTitle>Gastos registrados</CardTitle>
        </CardHeader>
        <CardContent>
          {rows.length ? (
            <div className="divide-y divide-slate-100">
              {rows.map((row) => (
                <div key={row.id} className="flex items-center justify-between gap-4 py-3 text-sm">
                  <div>
                    <p className="font-medium text-slate-950">{row.description}</p>
                    <p className="text-slate-500">
                      {formatDate(row.expense_date)} · {row.expense_type}
                    </p>
                  </div>
                  <p className="font-semibold text-slate-950">{formatCurrency(row.amount)}</p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="Sin gastos manuales" description="Agrega gastos en efectivo o movimientos fuera de tarjeta." />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
