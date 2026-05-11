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
  ai_analysis?: PdfAIAnalysis | null;
  message: string;
};

export type PdfAIAnalysis = {
  id: number;
  uploaded_file_id: number;
  model?: string | null;
  status: "pending" | "skipped" | "completed" | "error" | string;
  summary?: string | null;
  insights?: { title: string; detail: string; severity: "info" | "warning" | "critical" | string }[] | null;
  category_suggestions?: {
    description: string;
    suggested_category: string;
    expense_type: "fixed" | "variable" | "exceptional" | string;
    confidence: number;
    reason: string;
  }[] | null;
  anomalies?: { description: string; amount: number; reason: string }[] | null;
  error_message?: string | null;
  created_at: string;
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

export type ReportGroupBy = "month" | "year";
export type ReportRecordType = "all" | "income" | "expense";
export type ReportSource = "all" | "pdf" | "manual";

export type CashflowReportFilters = {
  group_by?: ReportGroupBy;
  record_type?: ReportRecordType;
  source?: ReportSource;
  expense_category_id?: number;
  income_category_id?: number;
  flow_type?: string;
  year?: number;
  month?: number;
  exact_date?: string;
  date_from?: string;
  date_to?: string;
  q?: string;
  limit?: number;
};

export type CashflowReportRow = {
  id: number;
  kind: "income" | "expense";
  source: "pdf" | "manual";
  date: string;
  period: string;
  description: string;
  category_id?: number | null;
  category: string;
  flow_type: string;
  amount: string | number;
  signed_amount: string | number;
  bank_name?: string | null;
  card_type?: string | null;
};

export type CashflowReport = {
  summary: {
    income: string | number;
    expenses: string | number;
    savings: string | number;
    savings_rate: number;
    row_count: number;
  };
  group_by: ReportGroupBy;
  groups: { key: string; label: string; income: string | number; expenses: string | number; savings: string | number; count: number }[];
  by_category: { key: string; label: string; kind: "income" | "expense"; amount: string | number; count: number }[];
  by_type: { key: string; label: string; kind: "income" | "expense"; amount: string | number; count: number }[];
  rows: CashflowReportRow[];
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
