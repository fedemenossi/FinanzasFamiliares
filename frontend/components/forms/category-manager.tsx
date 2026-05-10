"use client";

import { useState } from "react";
import { Pencil, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type ManagedCategory = {
  id: number;
  name: string;
  color?: string | null;
};

type Props<T extends ManagedCategory> = {
  rows: T[];
  createItem: (payload: { name: string; color?: string }) => Promise<unknown>;
  updateItem: (id: number, payload: { name?: string; color?: string; is_active?: boolean }) => Promise<unknown>;
  deleteItem: (id: number) => Promise<unknown>;
  onChanged: () => void;
  emptyTitle: string;
  emptyDescription: string;
};

export function CategoryManager<T extends ManagedCategory>({ rows, createItem, updateItem, deleteItem, onChanged, emptyTitle, emptyDescription }: Props<T>) {
  const [editing, setEditing] = useState<T | null>(null);
  const [name, setName] = useState("");
  const [color, setColor] = useState("#0f766e");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function startEdit(row: T) {
    setEditing(row);
    setName(row.name);
    setColor(row.color || "#0f766e");
    setError(null);
  }

  function reset() {
    setEditing(null);
    setName("");
    setColor("#0f766e");
    setError(null);
  }

  async function submit() {
    setLoading(true);
    setError(null);
    try {
      if (editing) {
        await updateItem(editing.id, { name, color });
      } else {
        await createItem({ name, color });
      }
      reset();
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar la categoria");
    } finally {
      setLoading(false);
    }
  }

  async function remove(id: number) {
    setLoading(true);
    setError(null);
    try {
      await deleteItem(id);
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo dar de baja la categoria");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>{editing ? "Editar categoria" : "Nueva categoria"}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Nombre</Label>
            <Input value={name} onChange={(event) => setName(event.target.value)} placeholder="Ej. Supermercado" />
          </div>
          <div className="space-y-2">
            <Label>Color</Label>
            <div className="flex gap-3">
              <Input className="w-20 p-1" type="color" value={color} onChange={(event) => setColor(event.target.value)} />
              <Input value={color} onChange={(event) => setColor(event.target.value)} />
            </div>
          </div>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <div className="flex gap-2">
            <Button onClick={() => void submit()} disabled={loading || !name.trim()}>
              {loading ? "Guardando..." : editing ? "Guardar cambios" : "Crear categoria"}
            </Button>
            {editing ? (
              <Button variant="outline" onClick={reset} disabled={loading}>
                Cancelar
              </Button>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Categorias activas</CardTitle>
        </CardHeader>
        <CardContent>
          {rows.length ? (
            <div className="divide-y divide-slate-100">
              {rows.map((row) => (
                <div key={row.id} className="flex items-center justify-between gap-4 py-3">
                  <div className="flex items-center gap-3">
                    <span className="h-3 w-3 rounded-full" style={{ backgroundColor: row.color || "#0f766e" }} />
                    <span className="text-sm font-medium text-slate-950">{row.name}</span>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => startEdit(row)}>
                      <Pencil className="mr-2 h-4 w-4" />
                      Editar
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => void remove(row.id)} disabled={loading}>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Baja
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title={emptyTitle} description={emptyDescription} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
