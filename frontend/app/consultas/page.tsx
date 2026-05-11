"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getCashflowReport, getCategories, getIncomeCategories } from "@/services/finance";
import type { CashflowReport, CashflowReportFilters, Category, IncomeCategory, ReportGroupBy, ReportRecordType, ReportSource } from "@/types/api";

const monthOptions = [
  { value: "1", label: "Enero" },
  { value: "2", label: "Febrero" },
  { value: "3", label: "Marzo" },
  { value: "4", label: "Abril" },
  { value: "5", label: "Mayo" },
  { value: "6", label: "Junio" },
  { value: "7", label: "Julio" },
  { value: "8", label: "Agosto" },
  { value: "9", label: "Septiembre" },
  { value: "10", label: "Octubre" },
  { value: "11", label: "Noviembre" },
  { value: "12", label: "Diciembre" }
];

type FilterState = {
  group_by: ReportGroupBy;
  record_type: ReportRecordType;
  source: ReportSource;
  expense_category_id: string;
  income_category_id: string;
  flow_type: string;
  year: string;
  month: string;
  exact_date: string;
  date_from: string;
  date_to: string;
  q: string;
};

const initialFilters: FilterState = {
  group_by: "month",
  record_type: "all",
  source: "all",
  expense_category_id: "",
  income_category_id: "",
  flow_type: "",
  year: "",
  month: "",
  exact_date: "",
  date_from: "",
  date_to: "",
  q: ""
};

export default function ConsultasPage() {
  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const [report, setReport] = useState<CashflowReport | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [incomeCategories, setIncomeCategories] = useState<IncomeCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load(nextFilters = filters) {
    setLoading(true);
    setError(null);
    try {
      const [reportData, expenseCategories, incomeCategoryRows] = await Promise.all([
        getCashflowReport(toApiFilters(nextFilters)),
        getCategories(),
        getIncomeCategories()
      ]);
      setReport(reportData);
      setCategories(expenseCategories);
      setIncomeCategories(incomeCategoryRows);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cargar la consulta");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  function update<K extends keyof FilterState>(key: K, value: FilterState[K]) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void load();
  }

  function reset() {
    setFilters(initialFilters);
    void load(initialFilters);
  }

  const periodRows = useMemo(
    () => report?.groups.map((row) => ({ ...row, income: Number(row.income), expenses: Number(row.expenses), savings: Number(row.savings) })) ?? [],
    [report]
  );
  const categoryRows = useMemo(
    () => report?.by_category.slice(0, 10).map((row) => ({ ...row, amount: Number(row.amount) })) ?? [],
    [report]
  );

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Consultas</h2>
        <p className="page-subtitle">Analiza ingresos y gastos por fecha de consumo, categoria, tipo, origen y periodo.</p>
      </div>

      <Card>
        <CardContent className="p-5">
          <form onSubmit={submit} className="grid gap-4 lg:grid-cols-4">
            <Field label="Agrupar por">
              <Select
                value={filters.group_by}
                onChange={(value) => update("group_by", value as ReportGroupBy)}
                options={[
                  { value: "month", label: "Mes" },
                  { value: "year", label: "Año" }
                ]}
              />
            </Field>
            <Field label="Mostrar">
              <Select
                value={filters.record_type}
                onChange={(value) => update("record_type", value as ReportRecordType)}
                options={[
                  { value: "all", label: "Ingresos y gastos" },
                  { value: "expense", label: "Solo gastos" },
                  { value: "income", label: "Solo ingresos" }
                ]}
              />
            </Field>
            <Field label="Origen">
              <Select
                value={filters.source}
                onChange={(value) => update("source", value as ReportSource)}
                options={[
                  { value: "all", label: "Todos" },
                  { value: "pdf", label: "PDFs" },
                  { value: "manual", label: "Manual" }
                ]}
              />
            </Field>
            <Field label="Tipo">
              <Select
                value={filters.flow_type}
                onChange={(value) => update("flow_type", value)}
                placeholder="Todos"
                options={[
                  { value: "fixed", label: "Fijo" },
                  { value: "variable", label: "Variable" },
                  { value: "exceptional", label: "Excepcional" }
                ]}
              />
            </Field>
            <Field label="Categoria de gasto">
              <Select
                value={filters.expense_category_id}
                onChange={(value) => update("expense_category_id", value)}
                placeholder="Todas"
                options={categories.map((category) => ({ value: String(category.id), label: category.name }))}
              />
            </Field>
            <Field label="Categoria de ingreso">
              <Select
                value={filters.income_category_id}
                onChange={(value) => update("income_category_id", value)}
                placeholder="Todas"
                options={incomeCategories.map((category) => ({ value: String(category.id), label: category.name }))}
              />
            </Field>
            <Field label="Año">
              <Input value={filters.year} onChange={(event) => update("year", event.target.value)} inputMode="numeric" placeholder="2026" />
            </Field>
            <Field label="Mes">
              <Select value={filters.month} onChange={(value) => update("month", value)} placeholder="Todos" options={monthOptions} />
            </Field>
            <Field label="Fecha exacta">
              <Input type="date" value={filters.exact_date} onChange={(event) => update("exact_date", event.target.value)} />
            </Field>
            <Field label="Desde">
              <Input type="date" value={filters.date_from} onChange={(event) => update("date_from", event.target.value)} />
            </Field>
            <Field label="Hasta">
              <Input type="date" value={filters.date_to} onChange={(event) => update("date_to", event.target.value)} />
            </Field>
            <Field label="Buscar">
              <Input value={filters.q} onChange={(event) => update("q", event.target.value)} placeholder="Descripcion o categoria" />
            </Field>
            <div className="flex gap-3 lg:col-span-4">
              <Button type="submit">Consultar</Button>
              <Button type="button" variant="outline" onClick={reset}>
                Limpiar
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {loading ? <p className="text-sm text-slate-500">Cargando consulta...</p> : null}

      {report ? (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Kpi title="Ingresos" value={formatCurrency(report.summary.income)} tone="positive" />
            <Kpi title="Gastos" value={formatCurrency(report.summary.expenses)} tone="negative" />
            <Kpi title="Resultado" value={formatCurrency(report.summary.savings)} tone={Number(report.summary.savings) >= 0 ? "positive" : "negative"} />
            <Kpi title="Ahorro" value={`${report.summary.savings_rate.toFixed(1)}%`} />
          </div>

          {report.rows.length ? (
            <>
              <div className="grid gap-6 xl:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Evolucion por periodo</CardTitle>
                  </CardHeader>
                  <CardContent className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={periodRows}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                        <YAxis tickFormatter={(value) => `$${Number(value) / 1000}k`} tick={{ fontSize: 12 }} />
                        <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                        <Legend />
                        <Bar dataKey="income" name="Ingresos" fill="#0f766e" radius={[6, 6, 0, 0]} />
                        <Bar dataKey="expenses" name="Gastos" fill="#dc2626" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Categorias principales</CardTitle>
                  </CardHeader>
                  <CardContent className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={categoryRows}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                        <YAxis tickFormatter={(value) => `$${Number(value) / 1000}k`} tick={{ fontSize: 12 }} />
                        <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                        <Bar dataKey="amount" name="Importe" radius={[6, 6, 0, 0]}>
                          {categoryRows.map((row) => (
                            <Cell key={row.key} fill={row.kind === "income" ? "#0f766e" : "#dc2626"} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardContent className="overflow-x-auto p-0">
                  <table className="w-full min-w-[1080px] text-left text-sm">
                    <thead className="border-b bg-slate-50 text-xs uppercase text-slate-500">
                      <tr>
                        <th className="px-4 py-3">Fecha</th>
                        <th className="px-4 py-3">Concepto</th>
                        <th className="px-4 py-3">Clase</th>
                        <th className="px-4 py-3">Categoria</th>
                        <th className="px-4 py-3">Tipo</th>
                        <th className="px-4 py-3">Origen</th>
                        <th className="px-4 py-3">Banco / tarjeta</th>
                        <th className="px-4 py-3 text-right">Importe</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {report.rows.map((row) => (
                        <tr key={`${row.kind}-${row.source}-${row.id}`}>
                          <td className="px-4 py-3 text-slate-500">{formatDate(row.date)}</td>
                          <td className="px-4 py-3 font-medium text-slate-950">{row.description}</td>
                          <td className="px-4 py-3">{row.kind === "income" ? "Ingreso" : "Gasto"}</td>
                          <td className="px-4 py-3 text-slate-600">{row.category}</td>
                          <td className="px-4 py-3 text-slate-600">{translateType(row.flow_type)}</td>
                          <td className="px-4 py-3 text-slate-600">{row.source === "pdf" ? "PDF" : "Manual"}</td>
                          <td className="px-4 py-3 text-slate-500">{[row.bank_name, row.card_type].filter(Boolean).join(" / ") || "-"}</td>
                          <td className={row.kind === "income" ? "px-4 py-3 text-right font-semibold text-teal-700" : "px-4 py-3 text-right font-semibold text-red-700"}>
                            {formatCurrency(row.amount)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CardContent>
              </Card>
            </>
          ) : (
            <EmptyState title="Sin resultados" description="Ajusta los filtros para encontrar ingresos o gastos." />
          )}
        </>
      ) : null}
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      {children}
    </div>
  );
}

function Kpi({ title, value, tone = "neutral" }: { title: string; value: string; tone?: "neutral" | "positive" | "negative" }) {
  const color = tone === "positive" ? "text-teal-700" : tone === "negative" ? "text-red-700" : "text-slate-950";
  return (
    <Card>
      <CardContent className="p-5">
        <p className="text-sm text-slate-500">{title}</p>
        <p className={`mt-2 text-2xl font-semibold ${color}`}>{value}</p>
      </CardContent>
    </Card>
  );
}

function toApiFilters(filters: FilterState): CashflowReportFilters {
  return {
    group_by: filters.group_by,
    record_type: filters.record_type,
    source: filters.source,
    expense_category_id: toNumber(filters.expense_category_id),
    income_category_id: toNumber(filters.income_category_id),
    flow_type: filters.flow_type || undefined,
    year: toNumber(filters.year),
    month: toNumber(filters.month),
    exact_date: filters.exact_date || undefined,
    date_from: filters.date_from || undefined,
    date_to: filters.date_to || undefined,
    q: filters.q || undefined,
    limit: 700
  };
}

function toNumber(value: string) {
  return value ? Number(value) : undefined;
}

function translateType(value: string) {
  const labels: Record<string, string> = {
    fixed: "Fijo",
    variable: "Variable",
    exceptional: "Excepcional"
  };
  return labels[value] ?? value;
}
