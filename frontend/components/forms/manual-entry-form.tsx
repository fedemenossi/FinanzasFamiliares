"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { createExpense, createIncome } from "@/services/finance";
import type { Category, IncomeCategory } from "@/types/api";

type Props = {
  mode: "income" | "expense";
  categories?: Category[];
  incomeCategories?: IncomeCategory[];
  onCreated?: () => void;
};

export function ManualEntryForm({ mode, categories = [], incomeCategories = [], onCreated }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function submit(formData: FormData) {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const date = String(formData.get("date"));
      const description = String(formData.get("description"));
      const amount = Number(formData.get("amount"));
      const notes = String(formData.get("notes") || "");
      if (mode === "income") {
        await createIncome({
          income_date: new Date(`${date}T00:00:00`).toISOString(),
          description,
          amount,
          notes,
          income_category_id: Number(formData.get("income_category_id")),
          income_type: String(formData.get("income_type") || "variable") as "fixed" | "variable"
        });
      } else {
        await createExpense({
          expense_date: new Date(`${date}T00:00:00`).toISOString(),
          description,
          amount,
          notes,
          category_id: Number(formData.get("category_id")) || null,
          expense_type: String(formData.get("expense_type") || "variable")
        });
      }
      setSuccess(true);
      onCreated?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{mode === "income" ? "Nuevo ingreso" : "Nuevo gasto manual"}</CardTitle>
      </CardHeader>
      <CardContent>
        <form action={submit} className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label>Fecha</Label>
            <Input name="date" type="date" required defaultValue={new Date().toISOString().slice(0, 10)} />
          </div>
          <div className="space-y-2">
            <Label>Importe</Label>
            <Input name="amount" type="number" min="0" step="0.01" required />
          </div>
          <div className="space-y-2 md:col-span-2">
            <Label>Descripcion</Label>
            <Input name="description" required />
          </div>
          {mode === "income" ? (
            <>
              <div className="space-y-2">
                <Label>Categoria</Label>
                <select name="income_category_id" className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" required>
                  <option value="">Seleccionar categoria</option>
                  {incomeCategories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label>Tipo</Label>
                <select name="income_type" className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" defaultValue="fixed" required>
                  <option value="fixed">Fijo</option>
                  <option value="variable">Variable</option>
                </select>
              </div>
            </>
          ) : null}
          {mode === "expense" ? (
            <>
              <div className="space-y-2">
                <Label>Categoria</Label>
                <select name="category_id" className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm">
                  <option value="">Sin categoria</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label>Tipo</Label>
                <select name="expense_type" className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm" defaultValue="variable">
                  <option value="variable">Variable</option>
                  <option value="fixed">Fijo</option>
                  <option value="exceptional">Excepcional</option>
                </select>
              </div>
            </>
          ) : null}
          <div className="space-y-2 md:col-span-2">
            <Label>Observaciones</Label>
            <Textarea name="notes" />
          </div>
          {error ? <p className="text-sm text-red-600 md:col-span-2">{error}</p> : null}
          {success ? <p className="text-sm text-teal-700 md:col-span-2">Registro guardado.</p> : null}
          <div className="md:col-span-2">
            <Button type="submit" disabled={loading}>
              {loading ? "Guardando..." : "Guardar"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
