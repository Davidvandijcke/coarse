import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "coarse — Free AI Paper Reviewer",
  description:
    "Get a detailed AI review of your academic paper in minutes. Free and open source.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 antialiased">{children}</body>
    </html>
  );
}
