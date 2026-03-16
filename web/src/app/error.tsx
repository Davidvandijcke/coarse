"use client";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div
      style={{
        background: "var(--board)",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
        textAlign: "center",
      }}
    >
      <p
        style={{
          fontFamily: "var(--font-serif)",
          fontSize: "1.625rem",
          fontWeight: 400,
          color: "var(--red-chalk)",
          margin: "0 0 0.75rem",
        }}
      >
        Something broke.
      </p>
      <p
        style={{
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "0.95rem",
          color: "var(--dust)",
          margin: "0 0 1.5rem",
          maxWidth: "400px",
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        {error.message || "An unexpected error occurred."}
      </p>
      <button
        onClick={reset}
        style={{
          background: "var(--red-chalk)",
          color: "var(--board)",
          border: "none",
          padding: "0.75rem 2rem",
          fontFamily: "var(--font-chalk)",
          fontSize: "1.1rem",
          fontWeight: 600,
          cursor: "pointer",
          borderRadius: "2px",
          marginBottom: "1rem",
        }}
      >
        Try again
      </button>
      <a
        href="/"
        style={{
          fontFamily: "var(--font-chalk)",
          fontSize: "1rem",
          color: "var(--yellow-chalk)",
          textDecoration: "none",
        }}
      >
        Go home &rarr;
      </a>
    </div>
  );
}
