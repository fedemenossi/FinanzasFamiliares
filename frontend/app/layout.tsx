import type { Metadata } from "next";
import "./globals.css";

import { AuthProvider } from "@/hooks/use-auth";

export const metadata: Metadata = {
  title: "Asistente Financiero Familiar IA",
  description: "Dashboard financiero familiar con procesamiento de resumenes bancarios argentinos"
};

export const dynamic = "force-dynamic";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "";

  return (
    <html lang="es">
      <body>
        <script
          dangerouslySetInnerHTML={{
            __html: `window.__AFFIA_CONFIG__ = ${JSON.stringify({ NEXT_PUBLIC_API_URL: apiUrl })};`
          }}
        />
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
