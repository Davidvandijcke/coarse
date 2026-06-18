// German (de) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts. Uses the informal "du" form throughout.

import type { Messages } from "@/lib/i18n";

export const de: Messages = {
  siteLanguageLabel: "Sprache der Seite",

  codeBlockCopied: "kopiert ✓",
  codeBlockCopy: "kopieren",

  headerTagline: "peer review ist ein öffentliches Gut.",
  navSetup: "einrichten",
  navSideBySide: "im Vergleich",
  navGithub: "github ↗",

  bannerPausedDefault: "Einreichungen sind vorübergehend pausiert.",
  bannerBusyPrefix: "Das System ist ausgelastet (",
  bannerBusySuffix: " Plätze belegt). Dein Review wird möglicherweise in die Warteschlange gestellt.",
  bannerFasterPrefix: "Für schnellere Ergebnisse nimm die CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "Hey ",
  heroGreetingSuffix: " kannst du dieses Paper reviewen?",
  heroHeading: "‘coarse!",
  heroLede:
    "KI-Agenten reviewen dein Paper und schreiben ein Gutachten. Die API-Kosten zahlst du direkt. Kein Account.",
  heroManifesto:
    "Akademische Peer Review läuft auf unbezahlter akademischer Arbeit. Andere haben beschlossen, daraus ein Geschäft zu machen. Das fanden wir nicht gut.",

  scoreVsOthers: "vs. andere KI-Reviewer",
  statCostNum: "< $2*",
  statCostLabel: "pro Review",
  statCostFootnote: "*meistens :)",
  statCommentsNum: "20+",
  statCommentsLabel: "detaillierte Kommentare",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "Open Source",

  comparePrefix: "Blind evaluiert gegen",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Schneidet besser ab bei Abdeckung, Genauigkeit und Tiefe -- zu einem Bruchteil der Kosten.",
  compareLink: "Sieh dir den Vergleich an →",

  formSubmitHeading: "Ein Paper einreichen",
  fieldPaper: "Paper",
  dropzoneAriaLabel: "Lade dein Paper hoch — zieh eine Datei hierher oder klick zum Durchsuchen",
  dropzoneInputAriaLabel: "Wähle eine Datei zum Hochladen",
  dropzoneReplaceSuffix: " MB — klick oder zieh, um zu ersetzen",
  dropzonePromptPrefix: "Zieh deine Datei hierher, oder ",
  dropzoneBrowse: "durchsuchen",
  dropzoneMaxSize: "Bis zu 50 MB",

  fieldEmail: "E-Mail ",
  fieldEmailQualifier: "(nur für das Web-Review)",
  emailPlaceholderUnavailable: "— nicht verfügbar —",
  emailPlaceholder: "du@universitaet.de",
  emailAriaLabel: "E-Mail-Adresse",
  emailHelperDisabled:
    "Der E-Mail-Versand ist vorübergehend gestört. Speichere deinen Review-Schlüssel beim Einreichen und schau in etwa einer Stunde wieder vorbei.",
  emailHelperPrefix:
    "Wir mailen dir, wenn es fertig ist. Schau in deinen Spam-Ordner, falls du es nicht siehst.",

  fieldKey: "OpenRouter-Schlüssel",
  fieldKeyGetOne: "hol dir einen →",
  keyOrPaste: "— oder füg einen Schlüssel ein —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter-API-Schlüssel",
  keyHelper:
    "OAuth-Schlüssel bleiben nur in diesem Tab und werden gelöscht, wenn du es schließt. Werden nie auf unseren Servern gespeichert.",

  fieldNotes: "Hinweise für den Reviewer",
  fieldNotesOptional: "(optional)",
  notesPlaceholder:
    "z. B. fokussiere dich bitte auf die Identifikationsstrategie in §3 — der Datenabschnitt ist noch ein Platzhalter.",
  notesAriaLabel: "Optionale Hinweise, um den Reviewer zu steuern",
  notesHelper: "Steuere, worauf der Reviewer achtet. Setzt das Bewertungsschema nicht außer Kraft.",

  costEstimating: "Kosten werden geschätzt...",
  costEstimatePrefix: "Geschätzte API-Kosten: $",
  costUnavailable: "Kostenschätzung für dieses Modell nicht verfügbar",

  turnstileFailedLine1Prefix:
    "Unsere Mensch-Prüfung konnte nicht abgeschlossen werden. Etwas blockiert oder verlangsamt ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — meistens ein strikter Datenschutzmodus des Browsers (etwa Safaris Tracking-Schutz oder Firefox ETP strikt), ein Inhalts-/Werbeblocker (Brave Shields, uBlock Origin auf manchen Listen) oder ein langsames oder gefiltertes Netzwerk.",
  turnstileFailedLine2Prefix: "Lade zuerst die Seite neu. Wenn es bestehen bleibt, erlaube ",
  turnstileFailedLine2Mid: " für ",
  turnstileFailedLine2Suffix:
    " (deaktiviere Inhaltsblocker oder lockere die Datenschutzeinstellungen), oder nimm einen anderen Browser. Bei einer Preview-URL muss das Deployment diesen Hostnamen eventuell auch auf der Allowlist des Cloudflare-Turnstile-Widgets haben.",
  turnstileFailedLine3Prefix: "Oder lass coarse lokal mit deinem eigenen OpenRouter-Schlüssel laufen: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  submitButton: "Mein Paper reviewen",
  submitButtonBusy: "Wird eingereicht...",
  submitOr: "oder",
  handoffButton: "Mit meinem Abo reviewen ▾",
  handoffButtonBusy: "Wird vorbereitet...",

  handoffUploading: "Paper wird hochgeladen...",
  handoffPreparing: "Übergabe wird vorbereitet...",

  explainReviewLabel: "Mein Paper reviewen:",
  explainReviewBody:
    " OpenRouter erledigt alles von Anfang bis Ende. Datei wird nach der Verarbeitung gelöscht. Der Review-Schlüssel funktioniert 90 Tage. Meistens unter $2.",
  explainSubscriptionLabel: "Mit meinem Abo reviewen:",
  explainSubscriptionPart1:
    "wir geben dir einen Shell-Befehl, der die vollständige coarse-Pipeline lokal mit ",
  explainSubscriptionYour: "deinem",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", oder",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "-Abo für das LLM-Reasoning ausführt.",
  explainSubscriptionPdf:
    "Du zahlst nur ~$0,10 für den lokalen Mistral-OCR-Schritt (mit deinem eigenen OpenRouter-Schlüssel); Nicht-PDF-Uploads (.tex, .md, .docx, …) überspringen OCR und brauchen keinen OpenRouter-Schlüssel.",
  explainSubscriptionNonPdf:
    "Deine Datei ist kein PDF, daher wird der Mistral-OCR-Schritt komplett übersprungen — der gesamte Lauf wird von deinem Abo abgedeckt, kein OpenRouter-Schlüssel nötig.",
  explainSubscriptionPart3: "Das Review erscheint auf dieser Seite, sobald es fertig ist.",
  explainDisclaimer:
    "Läuft lokal auf deinem eigenen Rechner mit deinem eigenen Claude-Code-, Codex- oder Gemini-CLI-Account. coarse.ink empfängt oder speichert deinen Provider-Login nicht, und die Bedingungen, Nutzungslimits und Organisationsrichtlinien deines Providers gelten. coarse.ink ist nicht mit Anthropic, OpenAI oder Google verbunden.",

  handoffReviewWithPrefix: "Reviewen mit ",
  handoffModelLabel: "Modell",
  handoffEffortLabel: "Aufwand",
  handoffPastePromptPrefix: "Füge diesen Prompt in dein ",
  handoffPastePromptSuffix: "-Terminal ein:",
  handoffRunHint:
    "Der Agent aktualisiert den coarse-review-Skill, führt das vollständige Review lokal aus und braucht dafür 10–25 Minuten. Dein Provider-Login bleibt auf deinem Rechner.",
  handoffKeyNeededPrefix:
    "Dein OpenRouter-Schlüssel muss zuerst auf deinem Rechner sein — exportiere ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: ", oder leg ihn in ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " oder ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    " ab. Wir leiten ihn nicht über den Browser, weil die Übergabe-URL im Chat-Log deines Agenten landet. Fehlt er, fragt der Agent danach.",
  handoffKeyNotNeeded:
    "Kein OpenRouter-Schlüssel für dieses Paper nötig — es ist kein PDF, daher läuft die Extraktion lokal ohne den Mistral-OCR-Schritt.",
  handoffReviewUrlIntro: "Sobald das Review fertig ist, erscheint es unter:",
  handoffInstallPrefix: "Hast du ",
  handoffInstallSuffix: " noch nicht? ",
  handoffInstallLink: "installier es →",

  findReviewHeading: "Ein Review finden",
  findReviewPlaceholder: "Füge deinen Review-Schlüssel, den vollständigen Review-Link oder die alte Review-ID ein...",
  findReviewAriaLabel: "Review-Schlüssel",
  findReviewButton: "Finden",

  footerPrivacy: "Datenschutz",
  footerTerms: "Bedingungen",
  footerContact: "Kontakt",

  noticeKeyMigrated:
    "Dein gespeicherter OpenRouter-Schlüssel wurde in einen Speicher verschoben, der nur für diesen Tab gilt. Er wird gelöscht, wenn du diesen Tab schließt.",
  errorLoginNoPersist:
    "Eingeloggt, aber der Schlüssel konnte nicht in diesem Tab behalten werden. Du musst ihn erneut einfügen, falls diese Seite neu lädt.",
  errorLoginFailed:
    "OpenRouter-Login fehlgeschlagen. Versuch es erneut oder füge einen Schlüssel manuell ein.",
  errorAuthFailed:
    "Authentifizierung fehlgeschlagen. Bei Preview-Deploys bedeutet das meistens, dass die im Browser zwischengespeicherten Basic-Auth-Daten beim Absenden des Formulars nicht mitgeschickt wurden. Lade den Tab neu (Cmd/Ctrl+Shift+R), melde dich erneut bei der Passwortabfrage an und versuch es noch einmal.",
  errorServiceUnavailable: "Dienst vorübergehend nicht verfügbar — versuch es in einer Minute erneut.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "Unser Mensch-Prüf-Widget konnte nicht laden — wahrscheinlich blockiert eine Browser-Erweiterung (Brave Shields, uBlock Origin, Firefox ETP strikt) challenges.cloudflare.com. Versuch, sie zu deaktivieren für ",
  errorTurnstileBlockedSuffix: ", oder lass coarse lokal laufen: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "Warte immer noch darauf, dass die Mensch-Prüfung lädt — gib ihr eine Sekunde und versuch es erneut.",
  errorPrepareUpload: "Vorbereiten des Uploads fehlgeschlagen",
  errorUploadFailed: "Datei-Upload fehlgeschlagen — versuch es erneut",
  errorSubmissionFailed: "Einreichung fehlgeschlagen",
  errorHandoffFailed: "Übergabe fehlgeschlagen",
  launchCommandCopied: "Befehl in die Zwischenablage kopiert. Füge ihn in dein Terminal ein.",
  launchOpeningCodex:
    "Codex-Desktop-App wird geöffnet — der Composer sollte vorausgefüllt sein. Drück auf Senden.",
  launchOpeningPrefix: "Wird geöffnet: ",
  launchOpeningSuffix: " — füge den Prompt aus deiner Zwischenablage ein (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    "-Desktop-App ging nicht auf. Wenn du nur die CLI-Version installiert hast, füge stattdessen die obigen Befehle in dein Terminal ein.",
  errorLoginCouldNotStartPrefix: "OpenRouter-Login konnte nicht starten: ",

  reviewLanguageLabel: "Sprache des Reviews",
  reviewLanguageAuto: "Automatisch — folge der Sprache des Papers",
  reviewLanguageHelper:
    "Standardmäßig die eigene Sprache des Papers; Zitate bleiben immer im Original.",
};
