"use client";

import { useEffect, useState } from "react";

import { CategoryManager } from "@/components/forms/category-manager";
import { createCategory, deleteCategory, getCategories, updateCategory } from "@/services/finance";
import type { Category } from "@/types/api";

export default function CategoriesPage() {
  const [rows, setRows] = useState<Category[]>([]);

  async function load() {
    setRows(await getCategories());
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Categorias de gastos</h2>
        <p className="page-subtitle">Administra las categorias usadas por gastos manuales y movimientos importados.</p>
      </div>
      <CategoryManager
        rows={rows}
        createItem={({ name, color }) => createCategory(name, color)}
        updateItem={updateCategory}
        deleteItem={deleteCategory}
        onChanged={() => void load()}
        emptyTitle="Sin categorias de gastos"
        emptyDescription="Crea categorias para clasificar gastos y movimientos."
      />
    </div>
  );
}
