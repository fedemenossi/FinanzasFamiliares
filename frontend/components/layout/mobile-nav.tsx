"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, CreditCard, FileUp, Wallet } from "lucide-react";

import { cn } from "@/lib/utils";

const items = [
  { href: "/dashboard", label: "Inicio", icon: BarChart3 },
  { href: "/uploads", label: "PDFs", icon: FileUp },
  { href: "/transactions", label: "Mov.", icon: CreditCard },
  { href: "/income", label: "Ingresos", icon: Wallet }
];

export function MobileNav() {
  const pathname = usePathname();
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 grid grid-cols-4 border-t border-slate-200 bg-white lg:hidden">
      {items.map((item) => {
        const Icon = item.icon;
        const active = pathname === item.href;
        return (
          <Link key={item.href} href={item.href} className={cn("flex flex-col items-center gap-1 px-2 py-2 text-xs text-slate-500", active && "text-teal-700")}>
            <Icon className="h-4 w-4" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
