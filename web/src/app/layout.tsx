import type { Metadata } from "next";
import { Young_Serif, Caveat, Space_Mono } from "next/font/google";
import "katex/dist/katex.min.css";
import "./globals.css";

const youngSerif = Young_Serif({
  subsets: ["latin"],
  variable: "--font-young-serif",
  weight: ["400"],
  display: "swap",
});

const caveat = Caveat({
  subsets: ["latin"],
  variable: "--font-caveat",
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const spaceMono = Space_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-space-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "\u2018coarse \u2014 AI peer review, of course.",
  description:
    "An open-source multi-agent AI system that reviews your academic paper like a real referee. Bring your own OpenRouter key. Usually under $2.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${youngSerif.variable} ${caveat.variable} ${spaceMono.variable}`} suppressHydrationWarning>
      <body>
        {/* SVG filter definitions for textured rules */}
        <svg width="0" height="0" style={{ position: "absolute" }}>
          <defs>
            <filter id="ink-rough">
              <feTurbulence type="turbulence" baseFrequency="0.04" numOctaves="4" result="noise" />
              <feDisplacementMap in="SourceGraphic" in2="noise" scale="2" xChannelSelector="R" yChannelSelector="G" />
            </filter>
          </defs>
        </svg>
        {children}
      </body>
    </html>
  );
}
