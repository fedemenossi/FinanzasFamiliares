"use client";

import { api, saveToken } from "@/services/api";
import type { User } from "@/types/api";

export async function login(email: string, password: string) {
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);
  const { data } = await api.post<{ access_token: string; token_type: string }>("/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" }
  });
  saveToken(data.access_token);
  return data;
}

export async function register(payload: { email: string; password: string; full_name?: string }) {
  const { data } = await api.post<User>("/auth/register", payload);
  return data;
}

export async function me() {
  const { data } = await api.get<User>("/auth/me");
  return data;
}
