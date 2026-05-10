export type User = {
  id: number;
  email: string;
  full_name?: string | null;
};

export type Category = {
  id: number;
  name: string;
  color?: string | null;
  is_active?: boolean;
};

export type Transaction = {
  id: number;
  transaction_date: string;
  raw_description: string;
  normalized_description: string;
  amount: string | number;
  currency: string;
  bank_name?: string | null;
  card_brand?: string | null;
  card_type?: string | null;
  card_last_digits?: string | null;
  is_installment: boolean;
  installment_current?: number | null;
  installment_total?: number | null;
  expense_type: "fixed" | "variable" | "exceptional" | string;
  category?: Category | null;
};

export type UploadedFile = {
  id: number;
  original_filename: string;
  bank_name?: string | null;
  statement_type?: string | null;
  status: string;
  error_message?: string | null;
  created_at: string;
};

export type UploadResult = {
  uploaded_file: UploadedFile;
  parser_name: string;
  bank_name?: string | null;
  statement_type?: string | null;
  extracted_count: number;
  created_count: number;
  duplicate_count: number;
  raw_text_chars: number;
  diagnostic_lines: string[];
  candidate_lines: string[];
  transactions: Transaction[];
  message: string;
};

export type ManualIncome = {
  id: number;
  income_date: string;
  income_category_id: number;
  income_category?: IncomeCategory | null;
  description: string;
  amount: string | number;
  income_type: "fixed" | "variable" | string;
  notes?: string | null;
};

export type IncomeCategory = {
  id: number;
  name: string;
  color?: string | null;
  is_active?: boolean;
};

export type ManualExpense = {
  id: number;
  expense_date: string;
  category_id?: number | null;
  description: string;
  amount: string | number;
  notes?: string | null;
  expense_type: string;
};

export type DashboardSummary = {
  income: string | number;
  expenses: string | number;
  savings: string | number;
  savings_rate: number;
  expenses_by_category: { category: string; amount: number }[];
  monthly_evolution: { month: string; income: number; expenses: number }[];
  fixed_vs_variable: { type: string; amount: number }[];
  top_expenses: { date: string; description: string; amount: number }[];
  frequent_merchants: { merchant: string; count: number }[];
  small_expenses: { description: string; count: number }[];
};

export type Insight = {
  level: "info" | "success" | "warning" | "danger";
  title: string;
  detail: string;
  metric?: number | null;
};

export type Budget = {
  id: number;
  category_id: number;
  year: number;
  month: number;
  amount: string | number;
  notes?: string | null;
  category?: Category | null;
  spent: string | number;
  remaining: string | number;
  usage_percent: number;
};
