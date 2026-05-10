"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login, register } from "@/services/auth";
import { useAuth } from "@/hooks/use-auth";

const authSchema = z.object({
  email: z.string().email("Email invalido"),
  password: z.string().min(6, "Minimo 6 caracteres"),
  full_name: z.string().optional()
});

type AuthFormValues = z.infer<typeof authSchema>;

type AuthCardProps = {
  mode: "login" | "register";
};

export function AuthCard({ mode }: AuthCardProps) {
  const router = useRouter();
  const { refresh } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const form = useForm<AuthFormValues>({
    resolver: zodResolver(authSchema),
    defaultValues: { email: "", password: "", full_name: "" }
  });

  async function onSubmit(values: AuthFormValues) {
    setError(null);
    setLoading(true);
    try {
      if (mode === "register") {
        if (!values.full_name || values.full_name.trim().length < 2) {
          form.setError("full_name", { message: "Ingresa tu nombre" });
          return;
        }
        await register({ email: values.email, password: values.password, full_name: values.full_name });
      }
      await login(values.email, values.password);
      await refresh();
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo completar la operacion");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>{mode === "login" ? "Ingresar" : "Crear cuenta"}</CardTitle>
        <CardDescription>
          {mode === "login" ? "Accede a tu tablero financiero familiar." : "Crea una cuenta para empezar a consolidar tus gastos."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
          {mode === "register" ? (
            <div className="space-y-2">
              <Label htmlFor="full_name">Nombre</Label>
              <Input id="full_name" {...form.register("full_name")} />
              <FieldError message={form.formState.errors.full_name?.message} />
            </div>
          ) : null}
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" autoComplete="email" {...form.register("email")} />
            <FieldError message={form.formState.errors.email?.message} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Contrasena</Label>
            <Input id="password" type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} {...form.register("password")} />
            <FieldError message={form.formState.errors.password?.message} />
          </div>
          {error ? <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
          <Button className="w-full" type="submit" disabled={loading}>
            {loading ? "Procesando..." : mode === "login" ? "Ingresar" : "Crear cuenta"}
          </Button>
        </form>
        <p className="mt-5 text-center text-sm text-slate-500">
          {mode === "login" ? "No tenes cuenta?" : "Ya tenes cuenta?"}{" "}
          <Link className="font-medium text-teal-700 hover:text-teal-800" href={mode === "login" ? "/register" : "/login"}>
            {mode === "login" ? "Crear cuenta" : "Ingresar"}
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}

function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return <p className="text-xs text-red-600">{message}</p>;
}
