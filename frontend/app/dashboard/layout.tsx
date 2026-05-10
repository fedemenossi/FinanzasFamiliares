import { PrivateLayout } from "@/components/layout/private-layout";
import { MobileNav } from "@/components/layout/mobile-nav";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <PrivateLayout>
      {children}
      <MobileNav />
    </PrivateLayout>
  );
}
