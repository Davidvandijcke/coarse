// Dutch (nl) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const nl: Messages = {
  siteLanguageLabel: "Sitetaal",

  codeBlockCopied: "gekopieerd ✓",
  codeBlockCopy: "kopiëren",

  headerTagline: "peer review is een publiek goed.",
  navSetup: "instellen",
  navSideBySide: "vergelijking",
  navGithub: "github ↗",

  bannerPausedDefault: "Inzendingen zijn tijdelijk gepauzeerd.",
  bannerBusyPrefix: "Het systeem is druk (",
  bannerBusySuffix: " plaatsen in gebruik). Je review komt mogelijk in de wachtrij.",
  bannerFasterPrefix: "Voor snellere resultaten, gebruik de CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "Hé ",
  heroGreetingSuffix: " kun je dit artikel reviewen?",
  heroHeading: "‘coarse!",
  heroLede:
    "AI-agents reviewen je artikel en schrijven een refereerrapport. Je betaalt de API-kosten rechtstreeks. Geen account.",
  heroManifesto:
    "Academische peer review draait op onbetaalde academische arbeid. Anderen besloten daar een verdienmodel van te maken. Dat vonden wij niks.",

  scoreVsOthers: "vs. andere AI-reviewers",
  statCostNum: "< $2*",
  statCostLabel: "per review",
  statCostFootnote: "*meestal :)",
  statCommentsNum: "20+",
  statCommentsLabel: "gedetailleerde opmerkingen",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "open source",

  comparePrefix: "Blind geëvalueerd tegen",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Scoort hoger op dekking, specificiteit en diepgang -- tegen een fractie van de kosten.",
  compareLink: "Bekijk de vergelijking →",

  formSubmitHeading: "Dien een artikel in",
  fieldPaper: "Artikel",
  dropzoneAriaLabel: "Upload je artikel — sleep een bestand hierheen of klik om te bladeren",
  dropzoneInputAriaLabel: "Kies een bestand om te uploaden",
  dropzoneReplaceSuffix: " MB — klik of sleep om te vervangen",
  dropzonePromptPrefix: "Sleep je bestand hierheen, of ",
  dropzoneBrowse: "bladeren",
  dropzoneMaxSize: "Tot 50 MB",

  fieldEmail: "E-mail ",
  fieldEmailQualifier: "(alleen voor webreview)",
  emailPlaceholderUnavailable: "— niet beschikbaar —",
  emailPlaceholder: "jij@universiteit.nl",
  emailAriaLabel: "E-mailadres",
  emailHelperDisabled:
    "E-mailbezorging ligt tijdelijk plat. Bewaar je reviewsleutel bij het indienen en kom over ongeveer een uur terug.",
  emailHelperPrefix:
    "We e-mailen je als het klaar is. Controleer je spammap als je het niet ziet.",

  fieldKey: "OpenRouter-sleutel",
  fieldKeyGetOne: "haal er een →",
  keyOrPaste: "— of plak een sleutel —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter API-sleutel",
  keyHelper:
    "OAuth-sleutels blijven alleen in dit tabblad en worden gewist als je het sluit. Worden nooit op onze servers bewaard.",

  fieldNotes: "Opmerkingen voor de reviewer",
  fieldNotesOptional: "(optioneel)",
  notesPlaceholder:
    "bijv. focus op de identificatiestrategie in §3 — de datasectie is nog een placeholder.",
  notesAriaLabel: "Optionele opmerkingen om de reviewer te sturen",
  notesHelper: "Stuur waar de reviewer op let. Overschrijft het beoordelingskader niet.",

  costEstimating: "Kosten schatten...",
  costEstimatePrefix: "Geschatte API-kosten: $",
  costUnavailable: "Kostenschatting niet beschikbaar voor dit model",

  turnstileFailedLine1Prefix:
    "Onze menscontrole kon niet worden voltooid. Iets blokkeert of vertraagt ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — meestal een strikte privacymodus van de browser (zoals Safari's trackingpreventie of Firefox ETP strikt), een content-/adblocker (Brave Shields, uBlock Origin op sommige lijsten), of een traag of gefilterd netwerk.",
  turnstileFailedLine2Prefix: "Probeer eerst de pagina te herladen. Als het aanhoudt, sta ",
  turnstileFailedLine2Mid: " toe voor ",
  turnstileFailedLine2Suffix:
    " (schakel contentblockers uit of versoepel de privacy-instellingen), of gebruik een andere browser. Op een preview-URL moet de deployment die hostnaam mogelijk ook op de allowlist van de Cloudflare Turnstile-widget staan.",
  turnstileFailedLine3Prefix: "Of draai coarse lokaal met je eigen OpenRouter-sleutel: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  submitButton: "Review mijn artikel",
  submitButtonBusy: "Indienen...",
  submitOr: "of",
  handoffButton: "Review met mijn abonnement ▾",
  handoffButtonBusy: "Voorbereiden...",

  handoffUploading: "Artikel uploaden...",
  handoffPreparing: "Overdracht voorbereiden...",

  explainReviewLabel: "Review mijn artikel:",
  explainReviewBody:
    " OpenRouter regelt alles van begin tot eind. Bestand wordt na verwerking verwijderd. Reviewsleutel werkt 90 dagen. Meestal minder dan $2.",
  explainSubscriptionLabel: "Review met mijn abonnement:",
  explainSubscriptionPart1:
    "we geven je een shell-commando dat de volledige coarse-pipeline lokaal draait met ",
  explainSubscriptionYour: "jouw",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", of",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "abonnement voor het LLM-redeneren.",
  explainSubscriptionPdf:
    "Je betaalt alleen ~$0,10 voor de lokale Mistral OCR-stap (met je eigen OpenRouter-sleutel); niet-PDF-uploads (.tex, .md, .docx, …) slaan OCR over en hebben geen OpenRouter-sleutel nodig.",
  explainSubscriptionNonPdf:
    "Je bestand is geen PDF, dus de Mistral OCR-stap wordt volledig overgeslagen — de hele run wordt gedekt door je abonnement, geen OpenRouter-sleutel nodig.",
  explainSubscriptionPart3: "De review verschijnt op deze pagina zodra die klaar is.",
  explainDisclaimer:
    "Draait lokaal op je eigen machine met je eigen Claude Code-, Codex- of Gemini CLI-account. coarse.ink ontvangt of bewaart je provider-login niet, en de voorwaarden, gebruikslimieten en organisatiebeleid van je provider zijn van toepassing. coarse.ink is niet gelieerd aan Anthropic, OpenAI of Google.",

  handoffReviewWithPrefix: "Review met ",
  handoffModelLabel: "model",
  handoffEffortLabel: "inspanning",
  handoffPastePromptPrefix: "Plak deze prompt in je ",
  handoffPastePromptSuffix: "-terminal:",
  handoffRunHint:
    "De agent vernieuwt de coarse-review-skill, draait de volledige review lokaal en doet er 10–25 minuten over. Je provider-login blijft op je machine.",
  handoffKeyNeededPrefix:
    "Je OpenRouter-sleutel moet eerst op je machine staan — exporteer ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: ", of zet hem in ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " of ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    ". We sturen hem niet via de browser omdat de overdrachts-URL in het chatlogboek van je agent terechtkomt. Ontbreekt hij, dan vraagt de agent erom.",
  handoffKeyNotNeeded:
    "Geen OpenRouter-sleutel nodig voor dit artikel — het is geen PDF, dus de extractie draait lokaal zonder de Mistral OCR-stap.",
  handoffReviewUrlIntro: "Zodra de review klaar is, verschijnt die op:",
  handoffInstallPrefix: "Heb je ",
  handoffInstallSuffix: " nog niet? ",
  handoffInstallLink: "installeer het →",

  findReviewHeading: "Zoek een review",
  findReviewPlaceholder: "Plak je reviewsleutel, volledige reviewlink of oude review-ID...",
  findReviewAriaLabel: "Reviewsleutel",
  findReviewButton: "Zoeken",

  footerPrivacy: "privacy",
  footerTerms: "voorwaarden",
  footerContact: "contact",

  noticeKeyMigrated:
    "Je opgeslagen OpenRouter-sleutel is verplaatst naar opslag die alleen voor dit tabblad geldt. Hij wordt gewist als je dit tabblad sluit.",
  errorLoginNoPersist:
    "Ingelogd, maar de sleutel kon niet in dit tabblad worden bewaard. Je moet hem opnieuw plakken als deze pagina herlaadt.",
  errorLoginFailed:
    "OpenRouter-login mislukt. Probeer het opnieuw of plak handmatig een sleutel.",
  errorAuthFailed:
    "Authenticatie mislukt. Op preview-deploys betekent dit meestal dat de in de browser opgeslagen Basic Auth-gegevens niet zijn meegestuurd bij het verzenden van het formulier. Vernieuw het tabblad (Cmd/Ctrl+Shift+R), log opnieuw in bij de wachtwoordprompt en probeer het opnieuw.",
  errorServiceUnavailable: "Service tijdelijk niet beschikbaar — probeer het over een minuut opnieuw.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "Onze menscontrole-widget kon niet laden — waarschijnlijk blokkeert een browserextensie (Brave Shields, uBlock Origin, Firefox ETP strikt) challenges.cloudflare.com. Probeer die uit te schakelen voor ",
  errorTurnstileBlockedSuffix: ", of draai coarse lokaal: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "Nog steeds aan het wachten tot de menscontrole laadt — geef het een seconde en probeer het opnieuw.",
  errorPrepareUpload: "Voorbereiden van upload mislukt",
  errorUploadFailed: "Uploaden van bestand mislukt — probeer het opnieuw",
  errorSubmissionFailed: "Inzending mislukt",
  errorHandoffFailed: "Overdracht mislukt",
  launchCommandCopied: "Commando naar klembord gekopieerd. Plak het in je terminal.",
  launchOpeningCodex:
    "Codex-desktopapp wordt geopend — de composer zou vooraf ingevuld moeten zijn. Druk op verzenden.",
  launchOpeningPrefix: "Bezig met openen van ",
  launchOpeningSuffix: " — plak de prompt vanaf je klembord (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    "-desktopapp ging niet open. Als je alleen de CLI-versie hebt geïnstalleerd, plak dan de bovenstaande commando's in je terminal.",
  errorLoginCouldNotStartPrefix: "OpenRouter-login kon niet starten: ",

  reviewLanguageLabel: "Reviewtaal",
  reviewLanguageAuto: "Automatisch — volg de taal van het artikel",
  reviewLanguageHelper:
    "Standaard de eigen taal van het artikel; citaten blijven altijd in het origineel.",
};
