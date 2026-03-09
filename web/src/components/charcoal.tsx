/**
 * Editorial rules and decorative elements (dark theme).
 */

/** Textured editorial horizontal rule */
export function CharcoalRule({ opacity = 1 }: { opacity?: number }) {
  return (
    <svg
      aria-hidden="true"
      style={{
        display: "block",
        width: "100%",
        height: "2px",
        flexShrink: 0,
        opacity,
      }}
    >
      <line
        x1="0"
        y1="1"
        x2="100%"
        y2="1"
        stroke="var(--chalk)"
        strokeWidth="0.5"
        opacity="0.35"
        filter="url(#ink-rough)"
      />
    </svg>
  );
}

/**
 * Hero decorative marks — subtle editorial annotations.
 * Faint red-pen/annotation marks suggesting academic review.
 */
export function HeroMarks() {
  return (
    <svg
      aria-hidden="true"
      style={{
        position: "absolute",
        top: 0,
        left: "-2.5rem",
        width: "calc(100% + 5rem)",
        height: "100%",
        pointerEvents: "none",
        overflow: "visible",
      }}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Margin bracket */}
      <path
        d="M 6 180 L 0 180 L 0 290 L 6 290"
        stroke="var(--yellow-chalk)"
        strokeWidth="1.5"
        fill="none"
        opacity="0.18"
      />

      {/* Circled passage */}
      <ellipse
        cx="100"
        cy="280"
        rx="75"
        ry="22"
        fill="none"
        stroke="var(--yellow-chalk)"
        strokeWidth="1.2"
        opacity="0.12"
        transform="rotate(-3 100 280)"
      />

      {/* Underline emphasis */}
      <line
        x1="130"
        y1="162"
        x2="320"
        y2="160"
        stroke="var(--yellow-chalk)"
        strokeWidth="1.5"
        opacity="0.15"
      />

      {/* Check mark */}
      <path
        d="M 520 170 L 535 188 L 568 150"
        stroke="var(--yellow-chalk)"
        strokeWidth="2"
        fill="none"
        opacity="0.12"
      />

      {/* Question mark */}
      <text
        x="580"
        y="290"
        fill="var(--yellow-chalk)"
        opacity="0.12"
        fontFamily="Georgia, serif"
        fontSize="28"
        fontStyle="italic"
      >
        ?
      </text>

      {/* Asterisk */}
      <text
        x="350"
        y="145"
        fill="var(--yellow-chalk)"
        opacity="0.15"
        fontFamily="Georgia, serif"
        fontSize="24"
        fontStyle="italic"
      >
        *
      </text>
    </svg>
  );
}

/**
 * Scattered background marks for status/review pages.
 */
export function PageMarks() {
  return (
    <svg
      aria-hidden="true"
      style={{
        position: "fixed",
        inset: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        overflow: "hidden",
        zIndex: 0,
      }}
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="none"
    >
      {/* Subtle margin lines */}
      <line
        x1="3%"
        y1="0"
        x2="3%"
        y2="100%"
        stroke="var(--yellow-chalk)"
        strokeWidth="0.5"
        opacity="0.06"
      />
      <line
        x1="97%"
        y1="0"
        x2="97%"
        y2="100%"
        stroke="var(--yellow-chalk)"
        strokeWidth="0.5"
        opacity="0.04"
      />
    </svg>
  );
}
