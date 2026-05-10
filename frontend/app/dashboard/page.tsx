"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Info, TrendingDown, TrendingUp, Wallet } from "lucide-react";

import { DashboardCharts } from "@/components/charts/dashboard-charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCurrency } from "@/lib/utils";
import { getDashboard, getInsights } from "@/services/finance";
import type { DashboardSummary, Insight } from "@/types/api";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [dashboard, insightRows] = await Promise.all([getDashboard(), getInsights()]);
        setData(dashboard);
        setInsights(insightRows);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No se pudo cargar el dashboard");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  if (loading) return <div className="page-shell text-sm text-slate-500">Cargando dashboard...</div>;
  if (error) return <div className="page-shell text-sm text-red-600">{error}</div>;
  if (!data) return <div className="page-shell"><EmptyState title="Sin datos" description="Carga ingresos o sube resumenes para construir el dashboard." /></div>;

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Resumen familiar</h2>
        <p className="page-subtitle">Lectura consolidada de ingresos, gastos, ahorro y comportamiento mensual.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Kpi title="Ingresos" value={formatCurrency(data.income)} icon={<Wallet className="h-4 w-4" />} />
        <Kpi title="Gastos" value={formatCurrency(data.expenses)} icon={<TrendingDown className="h-4 w-4" />} />
        <Kpi title="Ahorro neto" value={formatCurrency(data.savings)} icon={<TrendingUp className="h-4 w-4" />} />
        <Kpi title="% ahorro" value={`${data.savings_rate.toFixed(1)}%`} icon={<CheckCircle2 className="h-4 w-4" />} />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {insights.slice(0, 3).map((insight) => (
          <InsightCard key={`${insight.title}-${insight.detail}`} insight={insight} />
        ))}
      </div>

      <DashboardCharts data={data} />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top 10 gastos</CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleList rows={data.top_expenses.map((item) => ({ label: item.description, value: formatCurrency(item.amount) }))} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Gastos hormiga</CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleList rows={data.small_expenses.map((item) => ({ label: item.description, value: `${item.count} veces` }))} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Kpi({ title, value, icon }: { title: string; value: string; icon: React.ReactNode }) {
  return (
    <Card>
      <CardContent className="flex items-center justify-between p-5">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-md bg-teal-50 text-teal-700">{icon}</div>
      </CardContent>
    </Card>
  );
}

function InsightCard({ insight }: { insight: Insight }) {
  const Icon = insight.level === "danger" || insight.level === "warning" ? AlertTriangle : insight.level === "success" ? CheckCircle2 : Info;
  return (
    <Card>
      <CardContent className="flex gap-3 p-5">
        <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-700">
          <Icon className="h-4 w-4" />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-950">{insight.title}</p>
          <p className="mt-1 text-sm leading-6 text-slate-500">{insight.detail}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function SimpleList({ rows }: { rows: { label: string; value: string }[] }) {
  if (!rows.length) return <p className="text-sm text-slate-500">Sin datos suficientes.</p>;
  return (
    <div className="divide-y divide-slate-100">
      {rows.map((row) => (
        <div key={`${row.label}-${row.value}`} className="flex items-center justify-between gap-4 py-3 text-sm">
          <span className="truncate text-slate-700">{row.label}</span>
          <span className="shrink-0 font-medium text-slate-950">{row.value}</span>
        </div>
      ))}
    </div>
  );
}
