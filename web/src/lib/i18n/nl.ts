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
  bannerFasterPrefix: "Voor snellere resultaten, probeer de CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "Hé ",
  heroGreetingSuffix: " kun je dit artikel reviewen?",
  heroHeading: "‘coarse!",
  heroLede:
    "AI-agents reviewen je artikel en schrijven een refereerrapport. Je betaalt de API-kosten rechtstreeks. Geen account.",
  heroManifesto:
    "Academische peer review draait op onbetaalde academische arbeid. Anderen besloten daar een verdienmodel van te maken. Daar waren wij niet van gediend.",

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
  emailPlaceholder: "jij@universiteit.be",
  emailAriaLabel: "E-mailadres",
  emailHelperDisabled:
    "E-mailbezorging ligt tijdelijk plat. Bewaar je reviewsleutel bij het indienen en kom over een uurtje terug.",
  emailHelperPrefix:
    "We mailen je als het klaar is. Check je spamfolder als je het niet ziet.",

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
  notesHelper: "Stuur waar de reviewer op let. Overschrijft de rubric niet.",

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

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "Model",
  modelPickerUnavailableTitle: "Momenteel niet beschikbaar",
  modelPickerSearchPlaceholder: "Modellen zoeken...",
  modelPickerLoading: "Modellen laden...",
  modelPickerNoResults: "Geen modellen gevonden.",
  modelPickerSearch: "modellen zoeken...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "Verbonden met OpenRouter",
  openRouterLogOut: "Uitloggen",
  openRouterLogIn: "Inloggen met OpenRouter →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "Voor deze review is de volledige beveiligde reviewlink of reviewsleutel nodig.",
  statusLoadFailed: "Laden van de reviewstatus mislukt. Probeer het opnieuw.",
  statusCancelledByUser: "Review geannuleerd door gebruiker",
  statusLoading: "Laden",
  statusAccessTokenRequired: "Toegangstoken vereist.",
  statusNotFoundHeading: "Review niet gevonden.",
  statusNotFoundBody: "Controleer de reviewsleutel en probeer het opnieuw.",
  statusCancelConfirmHeading: "Review annuleren?",
  statusCancelConfirmBody: "Weet je het zeker? Je kunt je resultaten dan niet meer zien.",
  statusCancelling: "Annuleren...",
  statusYesCancel: "Ja, annuleren",
  statusGoBack: "Terug",
  statusLabelCancelled: "geannuleerd",
  statusLabelFailed: "mislukt",
  statusLabelReviewing: "bezig met reviewen",
  statusLabelQueued: "in wachtrij",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "Je artikel wordt gelezen.",
  statusQueuedHeading: "In de wachtrij.",
  statusRunningBody: "De reviewpipeline draait (meestal 30–60 minuten).",
  statusQueuedBody: "Je review staat in de wachtrij en begint zo.",
  statusEmailWhenDone: "We mailen je als het klaar is.",
  statusCancelledHeading: "Review geannuleerd.",
  statusCancelledBody:
    "De wachtende taak is als geannuleerd gemarkeerd. Als het werk al was begonnen, heeft de worker mogelijk wat tijd nodig om af te ronden.",
  statusFailedHeading: "Mislukt.",
  statusUnexpectedError: "Er is een onverwachte fout opgetreden.",
  statusResubmitPrefix: "Probeer het opnieuw in te dienen, of meld je probleem op ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: ".",
  statusTryAgain: "Opnieuw proberen →",
  statusKeyBoxSave: "Je reviewsleutel — bewaar deze",
  statusKeyBoxLegacy: "Oude reviewlink",
  statusCopied: "Gekopieerd",
  statusCopyLink: "Link kopiëren",
  statusRedirectNote: "Deze pagina verwijst je automatisch door zodra je review klaar is.",
  statusCancelReview: "Review annuleren",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "Voor deze review is de volledige beveiligde reviewlink of reviewsleutel nodig.",
  reviewClientLoadFailed: "Laden van de review mislukt. Probeer het opnieuw.",
  reviewClientLoading: "Laden",
  reviewClientNotFoundHeading: "Review niet gevonden.",
  reviewClientNotFoundBody: "Controleer je sleutel en probeer het opnieuw.",
  reviewClientSubmitNewPaper: "Dien een nieuw artikel in →",
  reviewClientAccessTokenRequired: "Toegangstoken vereist.",
  reviewClientBackHome: "Terug naar home →",
  reviewClientReadingHeading: "Je artikel wordt gelezen.",
  reviewClientQueuedHeading: "In de wachtrij.",
  reviewClientRunningBody: "Meestal 30–60 minuten. Deze pagina wordt automatisch bijgewerkt.",
  reviewClientQueuedBody: "De verwerking begint zo.",
  reviewClientFailedHeading: "Review mislukt.",
  reviewClientUnexpectedError: "Er is een onverwachte fout opgetreden.",
  reviewClientTryAgain: "Opnieuw proberen →",
  reviewClientCancelledHeading: "Review geannuleerd.",
  reviewClientCancelledBody: "Deze review is geannuleerd voordat die was voltooid.",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "Minder tonen",
  reviewShowMore: "Meer tonen",
  reviewShowInPaper: "Tonen in artikel",
  reviewMarkActive: "Markeren als actief",
  reviewMarkDone: "Markeren als afgehandeld",
  reviewDismiss: "Negeren",
  reviewDiscuss: "Bespreken",
  reviewDiscussTitle: "Bespreek deze opmerking met een AI-model",
  reviewShowDetails: "Details tonen",
  reviewStatusDone: "Afgehandeld",
  reviewStatusDismissed: "Genegeerd",
  reviewHide: "Verbergen",
  reviewFilterAll: "Alle",
  reviewFilterActive: "Actief",
  reviewFilterDone: "Afgehandeld",
  reviewFilterDismissed: "Genegeerd",
  reviewSidebarOverallFeedback: "Algemene feedback",
  reviewSidebarCommentsPrefix: "Opmerkingen (",
  reviewSidebarCommentsRemainingSuffix: " resterend)",
  reviewRemainingSuffix: " resterend",
  reviewDownload: "Downloaden",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "Printen / PDF",
  reviewHidePaper: "Artikel verbergen",
  reviewShowPaper: "Artikel tonen",
  reviewCopied: "Gekopieerd",
  reviewShare: "Delen",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "Sleep om het artikelpaneel te vergroten of verkleinen",
  reviewResizeTitle: "Sleep om formaat te wijzigen",
  reviewOfPrefix: "Review van ",
  reviewMetaModel: "Model",
  reviewMetaDate: "Datum",
  reviewMetaDomain: "Domein",
  reviewMetaTime: "Tijd",
  reviewMetaCost: "Kosten",
  reviewMetaReviewLanguage: "Reviewtaal",
  reviewMetaAutoDetectedSuffix: " · automatisch gedetecteerd",
  reviewOverallFeedbackHeading: "Algemene feedback",
  reviewDetailedCommentsPrefix: "Gedetailleerde opmerkingen (",
  reviewDetailedCommentsSuffix: ")",
  reviewGeneratedByPrefix: "Gegenereerd door ",
  reviewGeneratedBySuffix: ". Uiteraard.",
  reviewShareThisReview: "Deel deze review",
  reviewDeleteReview: "Review verwijderen",
  reviewDeleteConfirmHeading: "Review verwijderen?",
  reviewDeleteConfirmBody: "Weet je het zeker? Je kunt je resultaten dan niet meer zien.",
  reviewDeleting: "Verwijderen...",
  reviewYesDelete: "Ja, verwijderen",
  reviewGoBack: "Terug",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "Klopt deze kritiek eigenlijk wel?",
  chatExamplePrompt2: "Hoe moet ik mijn artikel aanpassen om dit te verhelpen?",
  chatExamplePrompt3: "Waar in het artikel is dit van toepassing?",
  chatNoResponse: "Geen reactie van het model. Probeer het opnieuw of wissel van model.",
  chatSessionExpired: "Je OpenRouter-sessie is verlopen. Log opnieuw in om verder te gaan.",
  chatSomethingWrong: "Er is iets misgegaan.",
  chatDiscussKicker: "Bespreken · ",
  chatKickerComment: "opmerking #",
  chatKickerOverallFeedback: "algemene feedback",
  chatDiscussAriaPrefix: "Bespreken: ",
  chatCloseAriaLabel: "Chat sluiten",
  chatDisconnectKeyTitle:
    "Koppel je OpenRouter-sleutel los (hij wordt niet buiten dit tabblad bewaard)",
  chatDisconnectKey: "Sleutel loskoppelen",
  chatInputPlaceholder: "Stel een vraag over deze opmerking…",
  chatMessageAriaLabel: "Bericht",
  chatStop: "Stoppen",
  chatSend: "Versturen",
  chatModelDisclosurePrefix: "Model: ",
  chatKeyGateIntro:
    "Verbind OpenRouter om over deze opmerking te chatten. Je sleutel gaat rechtstreeks naar OpenRouter — nooit naar onze servers — en wordt gewist als je dit tabblad sluit.",
  chatKeyGateOrPaste: "— of plak een sleutel —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "OpenRouter API-sleutel",
  chatKeyGateUseKey: "Sleutel gebruiken",
  chatKeyGateHelper:
    "OAuth-sleutels blijven alleen in dit tabblad en worden gewist als je het sluit. Worden nooit op onze servers bewaard.",
  chatEmptyHintPrefix: "Vraag wat je maar wilt over deze opmerking. Elk bericht stuurt ",
  chatEmptyHintFullPaper: "het volledige artikel",
  chatEmptyHintQuotedPassage: "de geciteerde passage en feedback",
  chatEmptyHintSuffix: " mee als context en draait op je OpenRouter-tegoed.",
  chatEmptyHintNoPaper:
    "De volledige artikeltekst wordt niet bewaard voor deze review, dus antwoorden zijn alleen gebaseerd op de geciteerde passage en feedback.",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "Geopend: ",
  handoffMenuOpenedPromptMid: " met de prompt vooraf ingevuld — voeg coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md toe en verstuur. (Prompt is ook gekopieerd, voor de zekerheid.)",
  handoffMenuOpenedPlainMid: " — voeg coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md toe en plak de gekopieerde prompt.",
  handoffMenuButtonTitle:
    "Stuur het artikel + de review naar je eigen AI-chat (Claude, ChatGPT, Gemini, Grok, DeepSeek)",
  handoffMenuButton: "Bespreken met je AI",
  handoffMenuDownloadsIntro: "Downloadt het artikel + de review en opent vervolgens:",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "Artikel",
  paperPanelDownload: "Downloaden",
  paperPanelDownloadAriaLabel: "Artikel-markdown downloaden",
  paperPanelCloseAriaLabel: "Artikelpaneel sluiten",
};
