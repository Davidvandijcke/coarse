"use client";

interface Props {
  apiKey: string;
  onLogin: () => void;
  onLogout: () => void;
  disabled?: boolean;
}

export default function OpenRouterLoginButton({ apiKey, onLogin, onLogout, disabled }: Props) {
  const isLoggedIn = apiKey.trim().length > 0;

  if (isLoggedIn) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          fontFamily: "var(--font-chalk)",
          fontSize: "1.05rem",
          color: "var(--yellow-chalk)",
        }}
      >
        <span aria-live="polite">Connected to OpenRouter</span>
        <button
          type="button"
          onClick={onLogout}
          style={{
            background: "transparent",
            color: "var(--dust)",
            border: "none",
            padding: 0,
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            textDecoration: "underline",
            cursor: "pointer",
          }}
        >
          Log out
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={onLogin}
      disabled={disabled}
      style={{
        background: "var(--yellow-chalk)",
        color: "var(--board)",
        border: "none",
        padding: "0.6rem 1.25rem",
        fontFamily: "var(--font-chalk)",
        fontSize: "1.05rem",
        fontWeight: 600,
        cursor: disabled ? "not-allowed" : "pointer",
        borderRadius: "2px",
        transition: "background 0.2s, color 0.2s",
      }}
    >
      Log in with OpenRouter →
    </button>
  );
}
