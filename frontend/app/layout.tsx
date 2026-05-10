import type { Metadata } from "next";
import "./globals.css";

import { AuthProvider } from "@/hooks/use-auth";

export const metadata: Metadata = {
  title: "Asistente Financiero Familiar IA",
  description: "Dashboard financiero familiar con procesamiento de resumenes bancarios argentinos"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
