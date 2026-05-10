"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { useAuth } from "@/hooks/use-auth";

export function PrivateLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { loading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!loading && !isAuthenticated) router.replace("/login");
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-sm text-slate-500">Cargando sesion...</div>;
  }

  if (!isAuthenticated) return null;

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="min-w-0 flex-1">
        <Topbar />
        <main>{children}</main>
      </div>
    </div>
  );
}
