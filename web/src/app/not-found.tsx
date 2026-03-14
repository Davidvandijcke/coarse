export default function NotFound() {
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
      <span
        style={{
          fontFamily: "var(--font-chalk)",
          fontSize: "5rem",
          fontWeight: 700,
          color: "var(--yellow-chalk)",
          lineHeight: 1,
          transform: "rotate(-2deg)",
          display: "block",
        }}
      >
        404
      </span>
      <p
        style={{
          fontFamily: "var(--font-serif)",
          fontSize: "1.625rem",
          fontWeight: 400,
          color: "var(--chalk-bright)",
          margin: "1.25rem 0 0.75rem",
        }}
      >
        Page not found.
      </p>
      <p
        style={{
          fontFamily: "Georgia, serif",
          fontStyle: "italic",
          fontSize: "0.9375rem",
          color: "var(--dust)",
          margin: "0 0 1.5rem",
        }}
      >
        The blackboard is blank here.
      </p>
      <a
        href="/"
        style={{
          fontFamily: "var(--font-chalk)",
          fontSize: "1.1rem",
          color: "var(--yellow-chalk)",
          textDecoration: "none",
        }}
      >
        Back to the board &rarr;
      </a>
    </div>
  );
}
