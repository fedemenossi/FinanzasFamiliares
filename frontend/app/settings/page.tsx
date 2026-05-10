"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";

export default function SettingsPage() {
  const { user } = useAuth();
  const apiUrl =
    typeof window !== "undefined"
      ? window.__AFFIA_CONFIG__?.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_URL || "No configurada"
      : process.env.NEXT_PUBLIC_API_URL || "No configurada";

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Configuracion</h2>
        <p className="page-subtitle">Parametros de conexion y cuenta.</p>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Cuenta</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <Row label="Usuario" value={user?.full_name || "-"} />
            <Row label="Email" value={user?.email || "-"} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>API</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <Row label="NEXT_PUBLIC_API_URL" value={apiUrl} />
            <Row label="Autenticacion" value="JWT localStorage" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3 last:border-0">
      <span className="text-slate-500">{label}</span>
      <span className="break-all text-right font-medium text-slate-950">{value}</span>
    </div>
  );
}
