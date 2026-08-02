import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://cvusd-calendar-atlas.speeddesigns.chatgpt.site"),
  title: "CVUSD Calendar Atlas",
  description:
    "Explore 12 months of public events from Castro Valley Unified School District calendars.",
  alternates: {
    canonical: "https://cvusd-calendar-atlas.speeddesigns.chatgpt.site",
  },
  openGraph: {
    title: "CVUSD Calendar Atlas",
    description:
      "One district, every public date—1,052 source-linked school events in a searchable calendar.",
    url: "https://cvusd-calendar-atlas.speeddesigns.chatgpt.site",
    siteName: "CVUSD Calendar Atlas",
    type: "website",
    images: [
      {
        url: "https://cvusd-calendar-atlas.speeddesigns.chatgpt.site/og.png",
        width: 1731,
        height: 909,
        alt: "CVUSD Calendar Atlas editorial calendar graphic",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "CVUSD Calendar Atlas",
    description:
      "One district, every public date—explore 12 months of source-linked CVUSD events.",
    images: ["https://cvusd-calendar-atlas.speeddesigns.chatgpt.site/og.png"],
  },
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
