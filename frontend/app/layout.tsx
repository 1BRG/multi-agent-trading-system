import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";
import { ThemeProvider } from "../components/ThemeProvider";

export const metadata: Metadata = {
  title: "AI Stock Lab",
  description: "AI-assisted stock analysis and backtesting platform",
  icons: {
    icon: "/icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(() => { try { const theme = localStorage.getItem('app-theme'); document.documentElement.dataset.theme = theme === 'light' ? 'light' : 'dark'; } catch (error) { document.documentElement.dataset.theme = 'dark'; } })();`,
          }}
        />
      </head>
      <body>
        <ThemeProvider />
        {children}
      </body>
    </html>
  );
}
