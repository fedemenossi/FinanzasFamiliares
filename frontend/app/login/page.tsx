import { AuthCard } from "@/components/forms/auth-card";

export default function LoginPage() {
  return (
    <main className="grid min-h-screen grid-cols-1 bg-background lg:grid-cols-[1fr_520px]">
      <section className="hidden bg-slate-950 px-12 py-10 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="text-sm font-semibold text-teal-300">Asistente Financiero Familiar IA</div>
        <div className="max-w-xl">
          <p className="mb-4 text-sm uppercase tracking-[0.2em] text-slate-400">Finanzas familiares</p>
          <h1 className="text-5xl font-semibold leading-tight">Entende en que se va el dinero sin cargar todo a mano.</h1>
          <p className="mt-5 text-base leading-7 text-slate-300">
            Consolida resumenes, clasifica gastos y transforma movimientos bancarios en decisiones claras.
          </p>
        </div>
        <p className="text-sm text-slate-500">MVP fintech para Argentina</p>
      </section>
      <section className="flex items-center justify-center px-4 py-10">
        <AuthCard mode="login" />
      </section>
    </main>
  );
}
