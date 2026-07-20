import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "BlueForge — Defensive Hardening Competition",
  description: "Defend. Harden. Compete. — papan skor lomba hardening realtime.",
  icons: {
    icon: "/blueforge-icon-256.png",
    shortcut: "/blueforge-icon-256.png",
    apple: "/blueforge-icon-256.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
