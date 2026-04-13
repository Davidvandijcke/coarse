import type { NextConfig } from "next";

// Next.js Fast Refresh uses eval() in dev, so 'unsafe-eval' is required there.
// Production keeps the strict policy.
const isDev = process.env.NODE_ENV !== "production";
const scriptSrc = [
  "script-src",
  "'self'",
  "'unsafe-inline'",
  isDev ? "'unsafe-eval'" : null,
  "https://www.googletagmanager.com",
  "https://cdnjs.cloudflare.com",
  // Cloudflare Turnstile api.js. Without this, the CSP silently
  // blocks the widget from loading and every user hits the "please
  // complete the human check" dead-end (#111).
  "https://challenges.cloudflare.com",
]
  .filter(Boolean)
  .join(" ");

const cspDirectives = [
  "default-src 'self'",
  scriptSrc,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  // pdf.js (loaded from cdnjs for client-side PDF token estimation in
  // estimateCost.ts) spawns a web worker from a blob: URL. Without an
  // explicit worker-src the CSP falls back to script-src, which has no
  // blob: entry, so cost estimation silently errors on strict browsers.
  "worker-src 'self' blob:",
  "font-src 'self'",
  "connect-src 'self' https://*.supabase.co wss://*.supabase.co https://openrouter.ai https://www.google-analytics.com https://analytics.google.com",
  // Turnstile renders its challenge UI inside an iframe served from
  // challenges.cloudflare.com; default-src 'self' would otherwise
  // block it, leaving a blank box in the form.
  "frame-src 'self' https://challenges.cloudflare.com",
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "object-src 'none'",
].join("; ");

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "Content-Security-Policy", value: cspDirectives },
          { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
    ];
  },
};

export default nextConfig;
