"use client";

import { useEffect, useState } from "react";

import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { getCategories } from "@/services/finance";
import type { Category } from "@/types/api";

export default function CategoriesPage() {
  const [rows, setRows] = useState<Category[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCategories().then(setRows).catch((err) => setError(err instanceof Error ? err.message : "No se pudieron cargar categorias"));
  }, []);

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Categorias</h2>
        <p className="page-subtitle">Catalogo usado por el clasificador de gastos.</p>
      </div>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {rows.length ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {rows.map((category) => (
            <Card key={category.id}>
              <CardContent className="flex items-center gap-3 p-5">
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: category.color ?? "#0f766e" }} />
                <span className="font-medium text-slate-950">{category.name}</span>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState title="Sin categorias" description="Las categorias se crean automaticamente al registrar el usuario." />
      )}
    </div>
  );
}
