"use client";

import { useEffect, useState } from "react";

import { CategoryManager } from "@/components/forms/category-manager";
import { getIncomeCategories, createIncomeCategory, updateIncomeCategory, deleteIncomeCategory } from "@/services/finance";
import type { IncomeCategory } from "@/types/api";

export default function IncomeCategoriesPage() {
  const [rows, setRows] = useState<IncomeCategory[]>([]);

  async function load() {
    setRows(await getIncomeCategories());
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="page-shell pb-24 lg:pb-6">
      <div>
        <h2 className="page-title">Categorias de ingresos</h2>
        <p className="page-subtitle">Administra las categorias disponibles para clasificar ingresos familiares.</p>
      </div>
      <CategoryManager
        rows={rows}
        createItem={createIncomeCategory}
        updateItem={updateIncomeCategory}
        deleteItem={deleteIncomeCategory}
        onChanged={() => void load()}
        emptyTitle="Sin categorias de ingresos"
        emptyDescription="Crea categorias para clasificar ingresos fijos o variables."
      />
    </div>
  );
}
