"use client";

import { api } from "@/services/api";
import type {
  Budget,
  CashflowReport,
  CashflowReportFilters,
  Category,
  DashboardSummary,
  IncomeCategory,
  Insight,
  ManualExpense,
  ManualIncome,
  Transaction,
  UploadedFile,
  UploadResult
} from "@/types/api";

export async function getDashboard() {
  const { data } = await api.get<DashboardSummary>("/dashboard/summary");
  return data;
}

export async function getCashflowReport(filters: CashflowReportFilters) {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, value]) => value !== undefined && value !== null && value !== "")
  );
  const { data } = await api.get<CashflowReport>("/reports/cashflow", { params });
  return data;
}

export async function getInsights() {
  const { data } = await api.get<Insight[]>("/insights");
  return data;
}

export async function getCategories() {
  const { data } = await api.get<Category[]>("/categories");
  return data;
}

export async function createCategory(name: string, color?: string) {
  const { data } = await api.post<Category>("/categories", { name, color });
  return data;
}

export async function updateCategory(id: number, payload: { name?: string; color?: string; is_active?: boolean }) {
  const { data } = await api.patch<Category>(`/categories/${id}`, payload);
  return data;
}

export async function deleteCategory(id: number) {
  await api.delete(`/categories/${id}`);
}

export async function getTransactions(query?: string) {
  const { data } = await api.get<Transaction[]>("/transactions", { params: query ? { q: query } : undefined });
  return data;
}

export async function updateTransaction(id: number, payload: { category_id?: number; normalized_description?: string; expense_type?: string }) {
  const { data } = await api.patch<Transaction>(`/transactions/${id}`, payload);
  return data;
}

export async function deleteTransaction(id: number) {
  // Backend actual todavia no expone DELETE /transactions/:id. Se deja preparado para cuando exista.
  await api.delete(`/transactions/${id}`);
}

export async function uploadPdf(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<UploadResult>("/files/upload", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
}

export async function getUploadedFiles() {
  const { data } = await api.get<UploadedFile[]>("/files");
  return data;
}

export async function getIncome() {
  const { data } = await api.get<ManualIncome[]>("/manual/income");
  return data;
}

export async function getIncomeCategories() {
  const { data } = await api.get<IncomeCategory[]>("/manual/income-categories");
  return data;
}

export async function createIncomeCategory(payload: { name: string; color?: string }) {
  const { data } = await api.post<IncomeCategory>("/manual/income-categories", payload);
  return data;
}

export async function updateIncomeCategory(id: number, payload: { name?: string; color?: string; is_active?: boolean }) {
  const { data } = await api.patch<IncomeCategory>(`/manual/income-categories/${id}`, payload);
  return data;
}

export async function deleteIncomeCategory(id: number) {
  await api.delete(`/manual/income-categories/${id}`);
}

export async function createIncome(payload: {
  income_date: string;
  income_category_id: number;
  description: string;
  amount: number;
  income_type: "fixed" | "variable";
  notes?: string;
}) {
  const { data } = await api.post<ManualIncome>("/manual/income", payload);
  return data;
}

export async function getExpenses() {
  const { data } = await api.get<ManualExpense[]>("/manual/expenses");
  return data;
}

export async function createExpense(payload: {
  expense_date: string;
  category_id?: number | null;
  description: string;
  amount: number;
  notes?: string;
  expense_type: string;
}) {
  const { data } = await api.post<ManualExpense>("/manual/expenses", payload);
  return data;
}

export async function getBudgets(year?: number, month?: number) {
  const { data } = await api.get<Budget[]>("/budgets", { params: { year, month } });
  return data;
}

export async function upsertBudget(payload: { category_id: number; year: number; month: number; amount: number; notes?: string }) {
  const { data } = await api.post<Budget>("/budgets", payload);
  return data;
}
