import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Reliability Workbench",
  description: "Benchmark and governance platform for tool-using agents"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
