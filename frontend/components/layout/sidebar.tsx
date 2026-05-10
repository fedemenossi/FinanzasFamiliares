"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  CreditCard,
  FileUp,
  FolderTree,
  Home,
  LogOut,
  ReceiptText,
  Settings,
  TrendingDown,
  Wallet
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/uploads", label: "PDFs", icon: FileUp },
  { href: "/transactions", label: "Movimientos", icon: CreditCard },
  { href: "/income", label: "Ingresos", icon: Wallet },
  { href: "/expenses", label: "Gastos", icon: TrendingDown },
  { href: "/categories", label: "Categorias", icon: FolderTree },
  { href: "/settings", label: "Configuracion", icon: Settings }
];

export function Sidebar() {
  const pathname = usePathname();
  const { logout } = useAuth();

  return (
    <aside className="hidden min-h-screen w-72 shrink-0 border-r border-slate-200 bg-slate-950 text-white lg:flex lg:flex-col">
      <div className="border-b border-slate-800 px-5 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-teal-600">
            <BarChart3 className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-semibold leading-5">Finanzas Familiares</p>
            <p className="text-xs text-slate-400">Asistente IA</p>
          </div>
        </div>
      </div>
      <nav className="flex flex-1 flex-col gap-1 px-3 py-4">
        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-900 hover:text-white",
                active && "bg-white text-slate-950 hover:bg-white hover:text-slate-950"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-slate-800 p-3">
        <Button variant="ghost" className="w-full justify-start text-slate-300 hover:bg-slate-900 hover:text-white" onClick={logout}>
          <LogOut className="mr-3 h-4 w-4" />
          Cerrar sesion
        </Button>
      </div>
    </aside>
  );
}
