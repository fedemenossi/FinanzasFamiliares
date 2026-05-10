"use client";

import axios, { AxiosError } from "axios";

function resolveApiUrl() {
  const runtimeUrl = typeof window !== "undefined" ? window.__AFFIA_CONFIG__?.NEXT_PUBLIC_API_URL : undefined;
  const buildUrl = process.env.NEXT_PUBLIC_API_URL;
  const url = runtimeUrl || buildUrl;
  if (url) return url.replace(/\/$/, "");
  if (process.env.NODE_ENV === "development") return "http://localhost:8000/api/v1";
  return "";
}

const API_URL = resolveApiUrl();
const TOKEN_KEY = "affia_token";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 120000
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string; message?: string }>) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      (error.message === "Network Error"
        ? `Network Error: no se pudo conectar con ${API_URL || "NEXT_PUBLIC_API_URL no configurada"}. Verifica NEXT_PUBLIC_API_URL y que el backend este publico.`
        : error.message) ||
      "Ocurrio un error";
    return Promise.reject(new Error(message));
  }
);

export function saveToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
