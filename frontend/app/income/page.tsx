"use client";

import { useEffect, useState } from "react";

import { ManualEntryForm } from "@/components/forms/manual-entry-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getIncome } from "@/services/finance";
import type { ManualIncome } from "@/types/api";

export default function IncomePage() {
  const [rows, setRows] = useState<ManualIncome[]>([]);

  async function load() {
    setRows(await getIncome());
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Ingresos</h2>
        <p className="page-subtitle">Registra sueldos, honorarios y otros ingresos familiares.</p>
      </div>
      <ManualEntryForm mode="income" onCreated={() => void load()} />
      <Card>
        <CardHeader>
          <CardTitle>Ingresos registrados</CardTitle>
        </CardHeader>
        <CardContent>
          {rows.length ? (
            <div className="divide-y divide-slate-100">
              {rows.map((row) => (
                <div key={row.id} className="flex items-center justify-between gap-4 py-3 text-sm">
                  <div>
                    <p className="font-medium text-slate-950">{row.description}</p>
                    <p className="text-slate-500">{formatDate(row.income_date)}</p>
                  </div>
                  <p className="font-semibold text-teal-700">{formatCurrency(row.amount)}</p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="Sin ingresos" description="Crea el primer ingreso para calcular ahorro y ratios." />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
