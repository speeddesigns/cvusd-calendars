import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CVUSD Calendar Atlas",
  description:
    "Explore 12 months of public events from Castro Valley Unified School District calendars.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
