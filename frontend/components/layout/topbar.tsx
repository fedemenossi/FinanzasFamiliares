"use client";

import { usePathname } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/use-auth";

const titles: Record<string, string> = {
  "/dashboard": "Dashboard financiero",
  "/uploads": "Subida de PDFs",
  "/consultas": "Consultas",
  "/transactions": "Movimientos",
  "/income": "Ingresos",
  "/expenses": "Gastos manuales",
  "/categories": "Categorias de gastos",
  "/income-categories": "Categorias de ingresos",
  "/settings": "Configuracion"
};

export function Topbar() {
  const pathname = usePathname();
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-background/95 backdrop-blur">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div>
          <p className="text-sm text-slate-500">Asistente Financiero Familiar IA</p>
          <h1 className="text-lg font-semibold text-slate-950">{titles[pathname] ?? "Finanzas"}</h1>
        </div>
        <div className="flex items-center gap-3">
          <Badge className="bg-teal-50 text-teal-700">MVP Fase 2</Badge>
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-slate-900">{user?.full_name || user?.email || "Usuario"}</p>
            <p className="text-xs text-slate-500">Cuenta familiar</p>
          </div>
        </div>
      </div>
    </header>
  );
}
