import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "abilithic DHC — Defensive Hardening Competition",
  description: "Defend. Harden. Compete. — papan skor lomba hardening realtime.",
  icons: {
    icon: "/abilithic-icon-256.png",
    shortcut: "/abilithic-icon-256.png",
    apple: "/abilithic-icon-256.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
