"use client";

import { cn } from "@/lib/utils";

type Option = {
  label: string;
  value: string;
};

type SelectProps = {
  value?: string;
  onChange?: (value: string) => void;
  options: Option[];
  placeholder?: string;
  className?: string;
};

export function Select({ value, onChange, options, placeholder, className }: SelectProps) {
  return (
    <select
      value={value ?? ""}
      onChange={(event) => onChange?.(event.target.value)}
      className={cn(
        "h-10 w-full rounded-md border border-input bg-white px-3 text-sm text-slate-950 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        className
      )}
    >
      {placeholder ? <option value="">{placeholder}</option> : null}
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
