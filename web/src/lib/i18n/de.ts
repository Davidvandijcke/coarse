// German (de) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts. Uses the informal "du" form throughout.

import type { Messages } from "@/lib/i18n";

export const de: Messages = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "Sprache der Seite",

  // copy-to-clipboard code block
  codeBlockCopied: "kopiert ✓",
  codeBlockCopy: "kopieren",

  // header
  headerTagline: "peer review ist ein öffentliches Gut.",
  navSetup: "einrichten",
  navSideBySide: "im Vergleich",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "Einreichungen sind vorübergehend pausiert.",
  bannerBusyPrefix: "Das System ist ausgelastet (",
  bannerBusySuffix: " Plätze belegt). Dein Review wird möglicherweise in die Warteschlange gestellt.",
  bannerFasterPrefix: "Für schnellere Ergebnisse nutze die CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "Hey ",
  heroGreetingSuffix: " kannst du dieses Paper reviewen?",
  heroHeading: "‘coarse!",
  heroLede:
    "KI-Agenten reviewen dein Paper und schreiben ein Gutachten. Die API-Kosten zahlst du direkt. Kein Account.",
  heroManifesto:
    "Akademische Peer Review läuft auf unbezahlter akademischer Arbeit. Andere haben beschlossen, daraus ein Geschäft zu machen. Das fanden wir nicht gut.",

  // hero — score preview
  scoreVsOthers: "vs. andere KI-Reviewer",
  statCostNum: "< $2*",
  statCostLabel: "pro Review",
  statCostFootnote: "*meistens :)",
  statCommentsNum: "20+",
  statCommentsLabel: "detaillierte Kommentare",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "Open Source",

  // hero — competitive comparison
  comparePrefix: "Blind getestet gegen",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Schneidet besser ab bei Abdeckung, Spezifität und Tiefe -- zu einem Bruchteil der Kosten.",
  compareLink: "Sieh dir den Vergleich an →",

  // submit form — section heading + paper field
  formSubmitHeading: "Ein Paper einreichen",
  fieldPaper: "Paper",
  dropzoneAriaLabel: "Lade dein Paper hoch — zieh eine Datei hierher oder klick zum Auswählen",
  dropzoneInputAriaLabel: "Wähle eine Datei zum Hochladen",
  dropzoneReplaceSuffix: " MB — klick oder zieh, um zu ersetzen",
  dropzonePromptPrefix: "Zieh deine Datei hierher, oder ",
  dropzoneBrowse: "durchsuchen",
  dropzoneMaxSize: "Bis zu 50 MB",

  // submit form — email field
  fieldEmail: "E-Mail ",
  fieldEmailQualifier: "(nur für das Web-Review)",
  emailPlaceholderUnavailable: "— nicht verfügbar —",
  emailPlaceholder: "du@universitaet.de",
  emailAriaLabel: "E-Mail-Adresse",
  emailHelperDisabled:
    "Der E-Mail-Versand ist vorübergehend gestört. Speichere deinen Review-Schlüssel beim Einreichen und schau in etwa einer Stunde wieder vorbei.",
  emailHelperPrefix:
    "Wir mailen dir, wenn es fertig ist. Schau in deinen Spam-Ordner, falls du es nicht siehst.",

  // submit form — OpenRouter key field
  fieldKey: "OpenRouter-Schlüssel",
  fieldKeyGetOne: "hol dir einen →",
  keyOrPaste: "— oder füg einen Schlüssel ein —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter-API-Schlüssel",
  keyHelper:
    "OAuth-Schlüssel bleiben nur in diesem Tab und werden gelöscht, wenn du ihn schließt. Werden nie auf unseren Servern gespeichert.",

  // submit form — author notes
  fieldNotes: "Hinweise für den Reviewer",
  fieldNotesOptional: "(optional)",
  notesPlaceholder:
    "z. B. fokussiere dich bitte auf die Identifikationsstrategie in §3 — der Datenabschnitt ist noch ein Platzhalter.",
  notesAriaLabel: "Optionale Hinweise, um den Reviewer zu steuern",
  notesHelper: "Steuere, worauf der Reviewer achtet. Setzt das Bewertungsschema nicht außer Kraft.",
  deepLiteratureLabel: "Vertiefte Literatursuche",
  deepLiteratureHelper:
    "Verwendet Perplexity Sonar Deep Research für eine gründlichere, mehrstufige Quellensuche. Fügt der Schätzung meist einige Minuten und etwa 0,30 $ hinzu.",
  deepLiteratureOn: "Ein",
  deepLiteratureOff: "Aus",

  // submit form — cost estimate
  costEstimating: "Kosten werden geschätzt...",
  costEstimatePrefix: "Geschätzte API-Kosten: $",
  costUnavailable: "Kostenschätzung für dieses Modell nicht verfügbar",

  // submit form — Turnstile failure block
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

  // submit form — buttons + handoff picker
  submitButton: "Mein Paper reviewen",
  submitButtonBusy: "Wird eingereicht...",
  submitOr: "oder",
  handoffButton: "Mit meinem Abo reviewen ▾",
  handoffButtonBusy: "Wird vorbereitet...",

  // submit form — handoff progress messages
  handoffUploading: "Paper wird hochgeladen...",
  handoffPreparing: "Übergabe wird vorbereitet...",

  // submit form — explanatory paragraphs
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
    "Die PDF-Verarbeitung nutzt deinen OpenRouter-Schlüssel für lokale Mistral-OCR und verursacht eine kleine Gebühr für die visuelle Qualitätsprüfung, wenn diese ausgeführt wird; Nicht-PDF-Uploads (.tex, .md, .docx, …) überspringen OCR und brauchen keinen OpenRouter-Schlüssel.",
  explainSubscriptionNonPdf:
    "Deine Datei ist kein PDF, daher wird der Mistral-OCR-Schritt komplett übersprungen — der gesamte Lauf wird von deinem Abo abgedeckt, kein OpenRouter-Schlüssel nötig.",
  explainSubscriptionPart3: "Das Review erscheint auf dieser Seite, sobald es fertig ist.",
  explainDisclaimer:
    "Läuft lokal auf deinem eigenen Rechner mit deinem eigenen Claude-Code-, Codex- oder Gemini-CLI-Account. coarse.ink empfängt oder speichert deinen Provider-Login nicht, und die Bedingungen, Nutzungslimits und Organisationsrichtlinien deines Providers gelten. coarse.ink ist nicht mit Anthropic, OpenAI oder Google verbunden.",

  // submit form — handoff result card
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

  // retrieve
  findReviewHeading: "Ein Review finden",
  findReviewPlaceholder: "Füge deinen Review-Schlüssel, den vollständigen Review-Link oder die alte Review-ID ein...",
  findReviewAriaLabel: "Review-Schlüssel",
  findReviewButton: "Finden",

  // footer
  footerPrivacy: "Datenschutz",
  footerTerms: "Bedingungen",
  footerContact: "Kontakt",

  // status / errors (set in handlers)
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

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "Sprache des Reviews",
  reviewLanguageAuto: "Automatisch — passt sich der Sprache des Papers an",
  reviewLanguageHelper:
    "Standardmäßig die Sprache des Papers selbst; Zitate bleiben immer im Original.",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "Modell",
  modelPickerUnavailableTitle: "Derzeit nicht verfügbar",
  modelPickerSearchPlaceholder: "Modelle suchen...",
  modelPickerLoading: "Modelle werden geladen...",
  modelPickerNoResults: "Keine Modelle gefunden.",
  modelPickerSearch: "Modelle suchen...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "Mit OpenRouter verbunden",
  openRouterLogOut: "Abmelden",
  openRouterLogIn: "Mit OpenRouter anmelden →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "Für dieses Review brauchst du den vollständigen sicheren Review-Link oder Review-Schlüssel.",
  statusLoadFailed: "Laden des Review-Status fehlgeschlagen. Versuch es erneut.",
  statusCancelledByUser: "Review vom Nutzer abgebrochen",
  statusLoading: "Lädt",
  statusAccessTokenRequired: "Zugriffstoken erforderlich.",
  statusNotFoundHeading: "Review nicht gefunden.",
  statusNotFoundBody: "Überprüfe den Review-Schlüssel und versuch es erneut.",
  statusCancelConfirmHeading: "Review abbrechen?",
  statusCancelConfirmBody: "Bist du sicher? Du wirst deine Ergebnisse nicht sehen können.",
  statusCancelling: "Wird abgebrochen...",
  statusYesCancel: "Ja, abbrechen",
  statusGoBack: "Zurück",
  statusLabelCancelled: "abgebrochen",
  statusLabelFailed: "fehlgeschlagen",
  statusLabelReviewing: "wird reviewt",
  statusLabelQueued: "in Warteschlange",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "Dein Paper wird gelesen.",
  statusQueuedHeading: "In der Warteschlange.",
  statusRunningBody: "Die Review-Pipeline läuft (meistens 30–60 Minuten).",
  statusQueuedBody: "Dein Review ist in der Warteschlange und startet in Kürze.",
  statusEmailWhenDone: "Wir mailen dir, wenn es fertig ist.",
  statusCancelledHeading: "Review abgebrochen.",
  statusCancelledBody:
    "Der wartende Job wurde als abgebrochen markiert. Falls die Arbeit bereits begonnen hatte, braucht der Worker eventuell etwas Zeit, um herunterzufahren.",
  statusFailedHeading: "Fehlgeschlagen.",
  statusUnexpectedError: "Ein unerwarteter Fehler ist aufgetreten.",
  statusResubmitPrefix: "Bitte versuch es erneut einzureichen, oder melde dein Problem auf ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: ".",
  statusTryAgain: "Erneut versuchen →",
  statusKeyBoxSave: "Dein Review-Schlüssel — speichere ihn",
  statusKeyBoxLegacy: "Alter Review-Link",
  statusCopied: "Kopiert",
  statusCopyLink: "Link kopieren",
  statusRedirectNote: "Diese Seite leitet automatisch weiter, sobald dein Review fertig ist.",
  statusCancelReview: "Review abbrechen",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "Für dieses Review brauchst du den vollständigen sicheren Review-Link oder Review-Schlüssel.",
  reviewClientLoadFailed: "Laden des Reviews fehlgeschlagen. Versuch es erneut.",
  reviewClientLoading: "Lädt",
  reviewClientNotFoundHeading: "Review nicht gefunden.",
  reviewClientNotFoundBody: "Überprüfe deinen Schlüssel und versuch es erneut.",
  reviewClientSubmitNewPaper: "Ein neues Paper einreichen →",
  reviewClientAccessTokenRequired: "Zugriffstoken erforderlich.",
  reviewClientBackHome: "Zurück zur Startseite →",
  reviewClientReadingHeading: "Dein Paper wird gelesen.",
  reviewClientQueuedHeading: "In der Warteschlange.",
  reviewClientRunningBody: "Meistens 30–60 Minuten. Diese Seite aktualisiert sich automatisch.",
  reviewClientQueuedBody: "Die Verarbeitung beginnt in Kürze.",
  reviewClientFailedHeading: "Review fehlgeschlagen.",
  reviewClientUnexpectedError: "Ein unerwarteter Fehler ist aufgetreten.",
  reviewClientTryAgain: "Erneut versuchen →",
  reviewClientCancelledHeading: "Review abgebrochen.",
  reviewClientCancelledBody: "Dieses Review wurde vor dem Abschluss abgebrochen.",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "Weniger anzeigen",
  reviewShowMore: "Mehr anzeigen",
  reviewShowInPaper: "Im Paper anzeigen",
  reviewMarkActive: "Als aktiv markieren",
  reviewMarkDone: "Als erledigt markieren",
  reviewDismiss: "Verwerfen",
  reviewDiscuss: "Besprechen",
  reviewDiscussTitle: "Diesen Kommentar mit einem KI-Modell besprechen",
  reviewShowDetails: "Details anzeigen",
  reviewStatusDone: "Erledigt",
  reviewStatusDismissed: "Verworfen",
  reviewHide: "Ausblenden",
  reviewFilterAll: "Alle",
  reviewFilterActive: "Aktiv",
  reviewFilterDone: "Erledigt",
  reviewFilterDismissed: "Verworfen",
  reviewSidebarOverallFeedback: "Gesamtbewertung",
  reviewSidebarCommentsPrefix: "Kommentare (",
  reviewSidebarCommentsRemainingSuffix: " übrig)",
  reviewRemainingSuffix: " übrig",
  reviewDownload: "Herunterladen",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "Drucken / PDF",
  reviewHidePaper: "Paper ausblenden",
  reviewShowPaper: "Paper anzeigen",
  reviewCopied: "Kopiert",
  reviewShare: "Teilen",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "Ziehen, um das Paper-Panel zu verkleinern oder vergrößern",
  reviewResizeTitle: "Ziehen zum Anpassen der Größe",
  reviewOfPrefix: "Review von ",
  reviewMetaModel: "Modell",
  reviewMetaDate: "Datum",
  reviewMetaDomain: "Bereich",
  reviewMetaTime: "Dauer",
  reviewMetaCost: "Kosten",
  reviewMetaReviewLanguage: "Sprache des Reviews",
  reviewMetaAutoDetectedSuffix: " · automatisch erkannt",
  reviewOverallFeedbackHeading: "Gesamtbewertung",
  reviewDetailedCommentsPrefix: "Detaillierte Kommentare (",
  reviewDetailedCommentsSuffix: ")",
  reviewGeneratedByPrefix: "Erstellt von ",
  reviewGeneratedBySuffix: ". Na klar.",
  reviewShareThisReview: "Dieses Review teilen",
  reviewDeleteReview: "Review löschen",
  reviewDeleteConfirmHeading: "Review löschen?",
  reviewDeleteConfirmBody: "Bist du sicher? Du wirst deine Ergebnisse nicht sehen können.",
  reviewDeleting: "Wird gelöscht...",
  reviewYesDelete: "Ja, löschen",
  reviewGoBack: "Zurück",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "Stimmt diese Kritik überhaupt?",
  chatExamplePrompt2: "Wie sollte ich überarbeiten, um darauf einzugehen?",
  chatExamplePrompt3: "Wo im Paper trifft das zu?",
  chatNoResponse: "Keine Antwort vom Modell. Versuch es erneut oder wechsle das Modell.",
  chatSessionExpired: "Deine OpenRouter-Sitzung ist abgelaufen. Melde dich erneut an, um fortzufahren.",
  chatSomethingWrong: "Etwas ist schiefgelaufen.",
  chatDiscussKicker: "Besprechen · ",
  chatKickerComment: "Kommentar Nr. ",
  chatKickerOverallFeedback: "Gesamtbewertung",
  chatDiscussAriaPrefix: "Besprechen: ",
  chatCloseAriaLabel: "Chat schließen",
  chatDisconnectKeyTitle:
    "Trenne deinen OpenRouter-Schlüssel (er wird nicht über diesen Tab hinaus gespeichert)",
  chatDisconnectKey: "Schlüssel trennen",
  chatInputPlaceholder: "Frag etwas zu diesem Kommentar…",
  chatMessageAriaLabel: "Nachricht",
  chatStop: "Stopp",
  chatSend: "Senden",
  chatModelDisclosurePrefix: "Modell: ",
  chatKeyGateIntro:
    "Verbinde OpenRouter, um über diesen Kommentar zu chatten. Dein Schlüssel geht direkt an OpenRouter — nie an unsere Server — und wird gelöscht, wenn du diesen Tab schließt.",
  chatKeyGateOrPaste: "— oder füg einen Schlüssel ein —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "OpenRouter-API-Schlüssel",
  chatKeyGateUseKey: "Schlüssel verwenden",
  chatKeyGateHelper:
    "OAuth-Schlüssel bleiben nur in diesem Tab und werden gelöscht, wenn du ihn schließt. Werden nie auf unseren Servern gespeichert.",
  chatEmptyHintPrefix: "Frag alles zu diesem Kommentar. Jede Nachricht sendet ",
  chatEmptyHintFullPaper: "das vollständige Paper",
  chatEmptyHintQuotedPassage: "die zitierte Passage und das Feedback",
  chatEmptyHintSuffix: " als Kontext und läuft auf deinem OpenRouter-Guthaben.",
  chatEmptyHintNoPaper:
    "Der vollständige Paper-Text ist für dieses Review nicht gespeichert, daher beruhen Antworten nur auf der zitierten Passage und dem Feedback.",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "Geöffnet: ",
  handoffMenuOpenedPromptMid: " mit vorausgefülltem Prompt — häng coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md an und sende dann. (Prompt wurde zur Sicherheit auch kopiert.)",
  handoffMenuOpenedPlainMid: " — häng coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md an und füge den kopierten Prompt ein.",
  handoffMenuButtonTitle:
    "Sende das Paper + Review an deinen eigenen KI-Chat (Claude, ChatGPT, Gemini, Grok, DeepSeek)",
  handoffMenuButton: "Mit deiner KI besprechen",
  handoffMenuDownloadsIntro: "Lädt das Paper + Review herunter und öffnet dann:",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "Paper",
  paperPanelDownload: "Herunterladen",
  paperPanelDownloadAriaLabel: "Paper-Markdown herunterladen",
  paperPanelCloseAriaLabel: "Paper-Panel schließen",

  // setup page (setup/page.tsx)
  // setup page — tab switcher
  setupTablistAriaLabel: "Einrichtungsweg",
  setupTabOpenRouter: "OpenRouter-Schlüssel",
  setupTabSubscription: "Mein Abo nutzen",
  // setup page — OpenRouter tab intro
  setupOrHeading: "Hol dir deinen OpenRouter-Schlüssel",
  setupOrIntro:
    "Dauert etwa 2 Minuten. Du brauchst eine Kreditkarte für ~$1 an Guthaben für den Start — in Schritt 2 lädst du auf $20 auf.",
  setupOrFasterLabel: "Schnellere Option:",
  setupOrFasterMid1: " im Hauptformular kannst du auf ",
  setupOrFasterLogIn: "„Mit OpenRouter anmelden“",
  setupOrFasterSuffix:
    " klicken, um coarse zu autorisieren und das manuelle Erstellen des Schlüssels zu überspringen. Du brauchst trotzdem einen OpenRouter-Account mit Guthaben (Schritte 1 und 2 unten), und wir empfehlen weiterhin, ein Ausgabenlimit pro Schlüssel zu setzen (Schritt 4).",
  // setup page — OpenRouter step 1
  setupOrStep1Title: "Erstelle einen Account",
  setupOrStep1BodyPrefix: "Geh zu ",
  setupOrStep1BodySuffix: " und klick auf „Get API Key“ oder registriere dich mit Google / GitHub.",
  setupOrStep1Annotation: "Startseite",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "Eine einheitliche API für LLMs — ein Schlüssel, viele Modelle.",
  // setup page — OpenRouter step 2
  setupOrStep2Title: "Guthaben hinzufügen",
  setupOrStep2BodyPrefix: "Navigiere zu ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    ". Füg mindestens $20 hinzu. Günstige Open-Source-Modelle kosten ~$0,25 pro Review; SOTA-Modelle wie Claude Opus oder GPT-5 können bei einem langen Paper $5–$10 kosten. Die vor dem Einreichen angezeigte Kostenschätzung ist ein Richtwert, keine Obergrenze. Lass Puffer, sonst kann das Review den Schlüssel auf halber Strecke aufbrauchen und fehlschlagen. Ungenutztes Guthaben verfällt nicht.",
  setupOrStep2Annotation: "Credits-Seite",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "Betrag",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "Guthaben: $0.00",
  // setup page — OpenRouter step 3
  setupOrStep3Title: "Erstelle einen API-Schlüssel",
  setupOrStep3BodyPrefix: "Geh zu ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: ", klick auf „Create Key“ und benenne ihn ",
  setupOrStep3BodySuffix: ".",
  setupOrStep3Provisioning:
    "Stell sicher, dass es ein regulärer API-Schlüssel ist — kein Provisioning-/Management-Schlüssel aus dem Integrations-Bereich. Provisioning-Schlüssel können andere Schlüssel erstellen und auflisten, aber keine Inferenz ausführen, und coarse schlägt mit „User not found“ fehl, wenn du so einen einfügst.",
  setupOrStep3CopyWarning: "Kopier den Schlüssel jetzt — du siehst ihn nicht noch einmal.",
  setupOrStep3Annotation: "Keys-Seite",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "Schlüsselname",
  setupOrStep3MockYourKey: "Dein Schlüssel",
  // setup page — OpenRouter step 4
  setupOrStep4Title: "Setz ein Ausgabenlimit für den Schlüssel",
  setupOrStep4BodyPrefix: "Auf der ",
  setupOrStep4BodyLink: "Keys-Seite",
  setupOrStep4BodyMid1: ", klick auf das ",
  setupOrStep4BodyMid2: "-Menü neben deinem neuen Schlüssel, wähle „Edit“ und setz das Guthabenlimit auf ",
  setupOrStep4BodyAtLeast: "mindestens $20",
  setupOrStep4BodySuffix:
    ". Der Schlüssel funktioniert nicht mehr, sobald das Limit erreicht ist, sodass überraschende Kosten unmöglich sind. Aber wenn du es zu knapp setzt, kann ein einziges teures Review es mitten im Lauf aufbrauchen.",
  setupOrStep4Annotation: "Schlüssel-Menü",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "Guthabenlimit für diesen Schlüssel",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "Warum das wichtig ist:",
  setupOrStep4WhyMid1: " coarse ist Open Source — du kannst ",
  setupOrStep4WhyLink: "jede Zeile Code lesen",
  setupOrStep4WhySuffix:
    ". Dein Schlüssel wird direkt an OpenRouter gesendet, um das Review auszuführen, und danach verworfen — er wird nie gespeichert. Aber du musst uns nicht vertrauen: Das Limit pro Schlüssel garantiert, dass er nie mehr ausgeben kann, als du erlaubst, selbst im schlimmsten Fall.",
  setupOrStep4CostLabel: "Ein Hinweis zu Kostenschätzungen:",
  setupOrStep4CostBody:
    " die vor dem Einreichen angezeigte Schätzung ist eine Heuristik mit einem Puffer von ~15 %, keine harte Obergrenze. Die tatsächlichen Kosten können bei SOTA-Modellen mit langen Papern bis zu ~2× der Schätzung betragen, sobald Beweisprüfung und Kritik-Umschreibungen einsetzen. Wenn die Obergrenze pro Schlüssel genau auf der Schätzung liegt, kann ein schwieriges Review sie aufbrauchen und mitten im Lauf fehlschlagen. Lass immer Puffer.",
  // setup page — OpenRouter step 5
  setupOrStep5Title: "Füg ihn in coarse ein",
  setupOrStep5Body: "Komm hierher zurück, füge deinen Schlüssel in das Formular ein und lade dein PDF hoch.",
  setupOrStep5Annotation: "coarse-Formular",
  setupOrStep5MockEmail: "E-Mail",
  setupOrStep5MockKey: "OpenRouter-Schlüssel",
  setupOrStep5MockButton: "Mein Paper reviewen",
  // setup page — shared footer CTA
  setupReadyCta: "Bereit? Reviewe dein Paper →",
  // setup page — subscription tab intro
  setupSubHeading: "Nutze dein Coding-Agent-Abo",
  setupSubIntro1:
    "Für Nutzer, die bereits für Claude Code, Codex oder Gemini CLI zahlen. Das Review läuft auf deinem Abo und wird dort abgerechnet. Du zahlst OpenRouter nur für die PDF-OCR und eine gegebenenfalls ausgelöste visuelle Qualitätsprüfung.",
  setupSubIntro2:
    "Läuft lokal auf deinem eigenen Rechner mit deinem eigenen Claude-Code-, Codex- oder Gemini-CLI-Account. coarse.ink empfängt oder speichert deinen Provider-Login nicht. Die Bedingungen und Nutzungslimits deines Providers gelten weiterhin. coarse.ink ist nicht mit Anthropic, OpenAI oder Google verbunden.",
  // setup page — subscription step 1
  setupSubStep1Title: "Installier einen Coding-Agenten",
  setupSubStep1Body:
    "Nimm den, für den du zahlst. Gemini CLI hat einen kostenlosen Tarif, falls nicht. Installier ihn von der Seite des Anbieters selbst — deren Doku bleibt aktuell.",
  setupSubStep1ClaudePrice: "Anthropic Pro oder Max",
  setupSubStep1CodexPrice: "ChatGPT Plus, Pro oder Business",
  setupSubStep1GeminiPrice: "Kostenloser Tarif reicht für die meisten Paper",
  setupSubStep1InstallLabel: "Installationsanleitung ↗",
  setupSubStep1Verify:
    "Führ den Test-Befehl aus, um Installation + Login zu prüfen. Wenn er eine Antwort ausgibt, bist du startklar.",
  setupSubStep1CardLogin: "Login: ",
  setupSubStep1CardTest: "Test: ",
  // setup page — subscription step 2
  setupSubStep2Title: "Leg einen OpenRouter-Schlüssel auf deinen Rechner (nur PDFs)",
  setupSubStep2BodyPrefix:
    "Dieser Schritt gilt nur für PDF-Paper — Nicht-PDF-Quellen (.tex, .md, .docx, …) werden lokal ohne OCR extrahiert, brauchen also nirgends einen OpenRouter-Schlüssel, und du kannst direkt zu Schritt 3 springen. Für PDFs braucht coarse OpenRouter für OCR und eine gegebenenfalls ausgelöste visuelle Qualitätsprüfung. Folge dem Tab ",
  setupSubStep2BodyTab: "OpenRouter-Schlüssel",
  setupSubStep2BodySuffix:
    ", um einen Account zu erstellen, $1 Guthaben hinzuzufügen und ein Limit von $2 pro Schlüssel zu setzen. Der $20-Puffer aus dem reinen OpenRouter-Weg ist hier nicht nötig, weil das Review selbst auf deinem Coding-Agent-Abo läuft.",
  setupSubStep2KeyPrefix: "Leg den Schlüssel dann auf deinen eigenen Rechner: führ ",
  setupSubStep2KeyMid1: " aus, leg ihn in eine ",
  setupSubStep2KeyMid2: " ab oder speichere ihn in ",
  setupSubStep2KeySuffix:
    ". Deine CLI liest ihn lokal, wenn sie die Extraktion ausführt; coarse.ink sieht ihn nie.",
  // setup page — subscription step 3
  setupSubStep3Title: "Lade dein Paper hoch und wähle eine CLI",
  setupSubStep3BodyPrefix: "Auf der ",
  setupSubStep3BodyLink: "Hauptseite",
  setupSubStep3BodyMid: ", zieh dein Paper (PDF, .tex, .md, .docx, …) auf das Formular und klick dann auf das Dropdown ",
  setupSubStep3BodyButton: "Mit meinem Abo reviewen ▾",
  setupSubStep3BodySuffix:
    " und wähle deine CLI. coarse lädt die Datei hoch, erzeugt ein Übergabe-Token und zeigt den Prompt, den du im nächsten Schritt einfügst. Du fügst deinen OpenRouter-Schlüssel hier nicht im Formular ein; die CLI liest ihn von deinem Rechner (Schritt 2).",
  // setup page — subscription step 4
  setupSubStep4Title: "Füg den Prompt in deine CLI ein",
  setupSubStep4BodyPrefix: "coarse gibt dir einen natürlichsprachlichen Prompt. Kopier ihn aus dem Panel, füge ihn in deine ",
  setupSubStep4BodyMid1: "-, ",
  setupSubStep4BodyMid2: "- oder ",
  setupSubStep4BodyMid3: "-Sitzung ein und drück auf Senden. Der Agent aktualisiert sein Skill-Bundle, führt die vollständige coarse-Pipeline über eigene Subprozess-Aufrufe aus und gibt eine ",
  setupSubStep4BodySuffix:
    "-URL aus, wenn er fertig ist. 10–25 Minuten. Klick auf die URL, um das fertige Review auf coarse.ink zu öffnen.",
  setupSubStep4TimeoutLabel: "Wenn du in einen Coding-Agenten einfügst",
  setupSubStep4TimeoutSuffix:
    " (kein einfaches Terminal), erhöh das Bash-Tool-Timeout auf mindestens 45 Min, bevor du den Prompt sendest. Standard-Timeouts von Agenten können bei nur 2 Min liegen, weit unter der Review-Laufzeit von 10–25 Min.",
  // setup page — subscription step 5 (troubleshooting)
  setupSubStep5Title: "Wenn etwas schiefgeht",
  setupSubTrouble1Symptom: "Der Button „Try opening Claude Code / Codex“ tut nichts.",
  setupSubTrouble1Fix:
    "Der Button funktioniert nur, wenn du die Desktop-App installiert hast. Bei einer reinen CLI-Installation kann der Browser kein Terminal für dich starten. Kopier den Prompt aus dem Panel und füge ihn manuell in deine CLI ein.",
  setupSubTrouble2Symptom: "„No such command ‚install-skills‘“ innerhalb des Agenten-Laufs.",
  setupSubTrouble2FixPrefix: "Kann ignoriert werden. Das Skill-Bundle wird trotzdem direkt über ",
  setupSubTrouble2FixSuffix: " geladen; der Agent macht mit dem Review-Schritt weiter.",
  setupSubTrouble3Symptom: "Meine Anthropic-/OpenAI-/Google-Rechnung ist nach einem Review gestiegen.",
  setupSubTrouble3FixPrefix: "Prüf auf ",
  setupSubTrouble3FixMid1: ", ",
  setupSubTrouble3FixMid2: " oder ",
  setupSubTrouble3FixSuffix:
    " in deiner Shell-Umgebung. Wenn gesetzt, rechnet die Host-CLI über den API-Account statt über dein Abo ab. v1.3.0+ entfernt diese automatisch, ältere Versionen taten das nicht.",
  setupSubTrouble4Symptom: "Weniger Kommentare als üblich (~10 statt 15–25).",
  setupSubTrouble4FixPrefix: "Ein Abschnitt hat das 30-Min-Timeout erreicht und wurde verworfen. Selten bei Standard-Aufwand, häufiger bei ",
  setupSubTrouble4FixSuffix:
    " bei langen Papern. Lass es erneut laufen; reduzier den Aufwand um eine Stufe, falls es zweimal passiert.",

  // compare page (ComparePage.tsx)
  comparePanelErrorBody: "Konnte dies nicht rendern. Versuch ein anderes Modell oder einen anderen Vergleich.",
  comparePaperCorticalCircuits: "Cortical Circuits",
  comparePaperCosetCodes: "Coset Codes",
  comparePaperPopulationGenetics: "Population Genetics",
  comparePaperTargetingInterventions: "Targeting Interventions",
  compareScoresShow: "Einblenden",
  compareScoresHide: "Ausblenden",
  compareScoresToggleSuffix: " aller Bewertungen über alle Paper ",
  compareScoresColPaper: "Paper",
  compareScoresColReference: "Referenz",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "Bewertet von Gemini 3.1 Pro mit multimodaler PDF-Eingabe. 5,0/5 = entspricht der Referenzqualität. 5,5+/5 = übertrifft sie.",
  compareJudgeShow: "Einblenden",
  compareJudgeHide: "Ausblenden",
  compareJudgeToggleSuffix: " des an Gemini 3.1 Pro gesendeten Judge-Prompts ",
  compareJudgeExplain:
    "Um bekannte Verzerrungen bei LLM-as-Judge abzumildern, wird der Judge pro Bewertung zweimal ausgeführt, wobei die beiden Reviews in der Darstellungsreihenfolge getauscht werden, und die Bewertungen werden über beide Reihenfolgen gemittelt. Das wirkt der Positionsverzerrung entgegen, bei der Judges systematisch das Review bevorzugen, das zuerst erscheint. Der Prompt enthält außerdem konkrete Anweisungen, um Verzerrung durch Wortfülle (Länge nicht über Substanz belohnen), Selbstsicherheits-Verzerrung (forsche Sprache nicht über korrektes Abwägen belohnen), Autoritäts-Verzerrung (Fachjargon oder Anzahl der Zitate nicht über Korrektheit belohnen) und Milde-Verzerrung (die volle Bewertungsspanne von 1–6 nutzen statt sich in der Mitte zu sammeln) entgegenzuwirken. Reviews werden neutral als „Review A“ und „Review B“ statt als „Referenz“ und „generiert“ bezeichnet, um eine Bewertung anhand der Herkunft zu verhindern.",
  compareJudgeSystemPromptLabel: "System-Prompt",
  compareJudgeUserPromptLabel: "User-Prompt (Paper + Reviews zur Laufzeit eingefügt)",
  compareVsMid: " vs ",
  compareScoreOutOf: "/5",
  compareMetricCoverage: "Abdeckung",
  compareMetricSpecificity: "Spezifität",
  compareMetricDepth: "Tiefe",
  compareJumpTo: "Springe zu",
  compareSectionOverallFeedback: "Gesamtbewertung",
  compareSectionDetailedComments: "Detaillierte Kommentare",
  compareVisitPrefix: "Besuche ",
  comparePdfReviewSuffix: "-Review",
  comparePdfFallback: "Lad das PDF herunter, falls der iframe nicht rendert ↓",
};
