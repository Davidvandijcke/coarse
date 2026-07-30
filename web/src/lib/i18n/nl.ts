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
  deepLiteratureLabel: "Diepgaand literatuuronderzoek",
  deepLiteratureHelper:
    "Gebruikt Perplexity Sonar Deep Research voor een grondigere, meerstaps bronzoektocht. Voegt meestal enkele minuten en ongeveer $ 0,30 toe aan de schatting.",
  deepLiteratureOn: "Aan",
  deepLiteratureOff: "Uit",

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

  // setup page (setup/page.tsx)
  // setup page — tab switcher
  setupTablistAriaLabel: "Setup-pad",
  setupTabOpenRouter: "OpenRouter-sleutel",
  setupTabSubscription: "Mijn abonnement gebruiken",
  // setup page — OpenRouter tab intro
  setupOrHeading: "Haal je OpenRouter-sleutel op",
  setupOrIntro:
    "Duurt ongeveer 2 minuten. Je hebt een kredietkaart nodig voor ~$1 aan tegoed om te starten — in stap 2 vul je aan tot $20.",
  setupOrFasterLabel: "Snellere optie:",
  setupOrFasterMid1: " op het hoofdformulier kun je klikken op ",
  setupOrFasterLogIn: "“Inloggen met OpenRouter”",
  setupOrFasterSuffix:
    " om coarse te autoriseren en het handmatig aanmaken van een sleutel over te slaan. Je hebt nog steeds een OpenRouter-account met tegoed nodig (stappen 1 en 2 hieronder), en we raden nog steeds aan om een uitgavenlimiet per sleutel in te stellen (stap 4).",
  // setup page — OpenRouter step 1
  setupOrStep1Title: "Maak een account aan",
  setupOrStep1BodyPrefix: "Ga naar ",
  setupOrStep1BodySuffix: " en klik op “Get API Key” of meld je aan met Google / GitHub.",
  setupOrStep1Annotation: "homepage",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "Eén uniforme API voor LLM's — één sleutel, veel modellen.",
  // setup page — OpenRouter step 2
  setupOrStep2Title: "Voeg tegoed toe",
  setupOrStep2BodyPrefix: "Navigeer naar ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    ". Voeg minstens $20 toe. Goedkope open-source modellen kosten ~$0,25 per review; SOTA-modellen zoals Claude Opus of GPT-5 kunnen op een lang artikel $5–$10 lopen. De kostenschatting die voor het indienen wordt getoond, is een ruwe inschatting, geen plafond. Laat speling over, anders kan de review de sleutel halverwege uitputten en mislukken. Ongebruikt tegoed verloopt niet.",
  setupOrStep2Annotation: "tegoedpagina",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "Bedrag",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "Saldo: $0.00",
  // setup page — OpenRouter step 3
  setupOrStep3Title: "Maak een API-sleutel aan",
  setupOrStep3BodyPrefix: "Ga naar ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: ", klik op “Create Key” en noem hem ",
  setupOrStep3BodySuffix: ".",
  setupOrStep3Provisioning:
    "Zorg dat het een gewone API-sleutel is — niet een provisioning-/managementsleutel uit de integraties-sectie. Provisioning-sleutels kunnen andere sleutels aanmaken en opsommen, maar kunnen geen inferentie draaien, en coarse mislukt met “User not found” als je er zo een plakt.",
  setupOrStep3CopyWarning: "Kopieer de sleutel nu — je krijgt hem niet opnieuw te zien.",
  setupOrStep3Annotation: "sleutelpagina",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "Sleutelnaam",
  setupOrStep3MockYourKey: "Je sleutel",
  // setup page — OpenRouter step 4
  setupOrStep4Title: "Stel een uitgavenlimiet in op de sleutel",
  setupOrStep4BodyPrefix: "Op de ",
  setupOrStep4BodyLink: "sleutelpagina",
  setupOrStep4BodyMid1: ", klik op het ",
  setupOrStep4BodyMid2: "-menu naast je nieuwe sleutel, kies “Edit” en stel de tegoedlimiet in op ",
  setupOrStep4BodyAtLeast: "minstens $20",
  setupOrStep4BodySuffix:
    ". De sleutel stopt met werken zodra de limiet is bereikt, dus onverwachte kosten zijn onmogelijk. Maar stel je hem te krap in, dan kan één dure review hem middenin uitputten.",
  setupOrStep4Annotation: "sleutelmenu",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "Tegoedlimiet voor deze sleutel",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "Waarom dit belangrijk is:",
  setupOrStep4WhyMid1: " coarse is open-source — je kunt ",
  setupOrStep4WhyLink: "elke regel code lezen",
  setupOrStep4WhySuffix:
    ". Je sleutel wordt rechtstreeks naar OpenRouter gestuurd om de review te draaien en daarna weggegooid — hij wordt nooit bewaard. Maar je hoeft ons niet te vertrouwen: de limiet per sleutel garandeert dat hij nooit meer kan uitgeven dan jij toestaat, zelfs in het slechtste geval.",
  setupOrStep4CostLabel: "Een opmerking over kostenschattingen:",
  setupOrStep4CostBody:
    " de schatting die voor het indienen wordt getoond, is een heuristiek met een buffer van ~15%, geen hard plafond. De werkelijke kosten op SOTA-modellen met lange artikels kunnen oplopen tot ~2× de schatting zodra proefverificatie en kritiekherschrijvingen op gang komen. Als de limiet per sleutel precies op de schatting zit, kan één lastige review hem leegmaken en middenin mislukken. Laat altijd speling over.",
  // setup page — OpenRouter step 5
  setupOrStep5Title: "Plak in coarse",
  setupOrStep5Body: "Kom hierheen terug, plak je sleutel in het formulier en upload je PDF.",
  setupOrStep5Annotation: "coarse-formulier",
  setupOrStep5MockEmail: "E-mail",
  setupOrStep5MockKey: "OpenRouter-sleutel",
  setupOrStep5MockButton: "Review mijn artikel",
  // setup page — shared footer CTA
  setupReadyCta: "Klaar? Review je artikel →",
  // setup page — subscription tab intro
  setupSubHeading: "Gebruik je coding-agent-abonnement",
  setupSubIntro1:
    "Voor gebruikers die al betalen voor Claude Code, Codex of Gemini CLI. De review draait op je abonnement en wordt daar gefactureerd. Je betaalt OpenRouter alleen ~$0,15 voor de OCR-stap.",
  setupSubIntro2:
    "Draait lokaal op je eigen machine met je eigen Claude Code-, Codex- of Gemini CLI-account. coarse.ink ontvangt of bewaart je provider-login niet. De voorwaarden en gebruikslimieten van je provider blijven van toepassing. coarse.ink is niet gelieerd aan Anthropic, OpenAI of Google.",
  // setup page — subscription step 1
  setupSubStep1Title: "Installeer een coding-agent",
  setupSubStep1Body:
    "Kies de agent waarvoor je betaalt. Gemini CLI heeft een gratis laag als je dat niet doet. Installeer hem vanaf de eigen pagina van de leverancier — hun docs blijven actueel.",
  setupSubStep1ClaudePrice: "Anthropic Pro of Max",
  setupSubStep1CodexPrice: "ChatGPT Plus, Pro of Business",
  setupSubStep1GeminiPrice: "Gratis laag volstaat voor de meeste artikels",
  setupSubStep1InstallLabel: "Installatie-instructies ↗",
  setupSubStep1Verify:
    "Draai het testcommando om installatie + login te verifiëren. Als het een reactie afdrukt, ben je klaar.",
  setupSubStep1CardLogin: "login: ",
  setupSubStep1CardTest: "test: ",
  // setup page — subscription step 2
  setupSubStep2Title: "Zet een OpenRouter-sleutel op je machine (alleen PDF's)",
  setupSubStep2BodyPrefix:
    "Deze stap geldt alleen voor PDF-artikels — niet-PDF-bronnen (.tex, .md, .docx, …) worden lokaal geëxtraheerd zonder OCR, dus die hebben nergens een OpenRouter-sleutel nodig en je kunt meteen door naar stap 3. Voor PDF's heeft coarse OpenRouter nog steeds nodig voor de OCR-stap (~$0,10 per artikel). Volg het tabblad ",
  setupSubStep2BodyTab: "OpenRouter-sleutel",
  setupSubStep2BodySuffix:
    " om een account aan te maken, $1 tegoed toe te voegen en een limiet van $2 per sleutel in te stellen. De buffer van $20 uit het OpenRouter-only pad is hier niet nodig, omdat de review zelf op je coding-agent-abonnement draait.",
  setupSubStep2KeyPrefix: "Zet de sleutel daarna op je eigen machine: draai ",
  setupSubStep2KeyMid1: ", zet hem in een ",
  setupSubStep2KeyMid2: ", of bewaar hem in ",
  setupSubStep2KeySuffix:
    ". Je CLI leest hem lokaal wanneer die de extractie draait; coarse.ink ziet hem nooit.",
  // setup page — subscription step 3
  setupSubStep3Title: "Upload je artikel en kies een CLI",
  setupSubStep3BodyPrefix: "Op de ",
  setupSubStep3BodyLink: "hoofdpagina",
  setupSubStep3BodyMid: ", sleep je artikel (PDF, .tex, .md, .docx, …) op het formulier en klik daarna op de dropdown ",
  setupSubStep3BodyButton: "Review met mijn abonnement ▾",
  setupSubStep3BodySuffix:
    " en kies je CLI. coarse uploadt het bestand, maakt een overdrachtstoken aan en toont de prompt die je in de volgende stap plakt. Je plakt je OpenRouter-sleutel hier niet op het formulier; de CLI leest hem van je machine (stap 2).",
  // setup page — subscription step 4
  setupSubStep4Title: "Plak de prompt in je CLI",
  setupSubStep4BodyPrefix: "coarse geeft je één prompt in natuurlijke taal. Kopieer hem uit het paneel, plak hem in je ",
  setupSubStep4BodyMid1: ", ",
  setupSubStep4BodyMid2: ", of ",
  setupSubStep4BodyMid3: "-sessie en druk op verzenden. De agent vernieuwt zijn skill-bundel, draait de volledige coarse-pipeline op zijn eigen subprocess-calls en drukt een ",
  setupSubStep4BodySuffix:
    "-URL af als die klaar is. 10–25 minuten. Klik op de URL om de voltooide review op coarse.ink te openen.",
  setupSubStep4TimeoutLabel: "Als je in een coding-agent plakt",
  setupSubStep4TimeoutSuffix:
    " (geen gewone terminal), verhoog dan de timeout van zijn bash-tool naar minstens 45 min voordat je de prompt verstuurt. Standaard agent-timeouts kunnen zo laag als 2 min zijn, ver onder de reviewlooptijd van 10–25 min.",
  // setup page — subscription step 5 (troubleshooting)
  setupSubStep5Title: "Als er iets misgaat",
  setupSubTrouble1Symptom: "De knop “Probeer Claude Code / Codex te openen” doet niets.",
  setupSubTrouble1Fix:
    "De knop werkt alleen als je de desktopapp hebt geïnstalleerd. Met een CLI-only installatie kan de browser geen terminal voor je starten. Kopieer de prompt uit het paneel en plak hem handmatig in je CLI.",
  setupSubTrouble2Symptom: "“No such command ‘install-skills’” binnen de agent-run.",
  setupSubTrouble2FixPrefix: "Veilig te negeren. De skill-bundel laadt nog steeds rechtstreeks via ",
  setupSubTrouble2FixSuffix: "; de agent gaat door naar de reviewstap.",
  setupSubTrouble3Symptom: "Mijn Anthropic-/OpenAI-/Google-rekening ging omhoog na een review.",
  setupSubTrouble3FixPrefix: "Controleer op ",
  setupSubTrouble3FixMid1: ", ",
  setupSubTrouble3FixMid2: ", of ",
  setupSubTrouble3FixSuffix:
    " in je shell-omgeving. Als die is ingesteld, factureert de host-CLI het API-account in plaats van je abonnement. v1.3.0+ verwijdert deze automatisch, maar oudere versies deden dat niet.",
  setupSubTrouble4Symptom: "Minder opmerkingen dan gebruikelijk (~10 in plaats van 15–25).",
  setupSubTrouble4FixPrefix: "Een sectie liep tegen de timeout van 30 min aan en is weggevallen. Zeldzaam bij standaardinspanning, vaker met ",
  setupSubTrouble4FixSuffix:
    " op lange artikels. Draai opnieuw; verlaag de inspanning één stap als het twee keer gebeurt.",

  // compare page (ComparePage.tsx)
  comparePanelErrorBody: "Kon deze niet weergeven. Probeer een ander model of een andere vergelijking.",
  comparePaperCorticalCircuits: "Cortical Circuits",
  comparePaperCosetCodes: "Coset Codes",
  comparePaperPopulationGenetics: "Population Genetics",
  comparePaperTargetingInterventions: "Targeting Interventions",
  compareScoresShow: "Toon",
  compareScoresHide: "Verberg",
  compareScoresToggleSuffix: " alle scores over alle artikels ",
  compareScoresColPaper: "Artikel",
  compareScoresColReference: "Referentie",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "Geëvalueerd door Gemini 3.1 Pro met multimodale PDF-invoer. 5.0/5 = evenaart de referentiekwaliteit. 5.5+/5 = overtreft die.",
  compareJudgeShow: "Toon",
  compareJudgeHide: "Verberg",
  compareJudgeToggleSuffix: " de juryprompt die naar Gemini 3.1 Pro is gestuurd ",
  compareJudgeExplain:
    "Om bekende biases van LLM-als-jury tegen te gaan, wordt de jury per evaluatie twee keer gedraaid met de twee reviews in omgekeerde presentatievolgorde, en worden de scores over beide volgordes gemiddeld. Dit counteret positionele bias, waarbij jury's systematisch de review verkiezen die als eerste verschijnt. De prompt bevat ook specifieke instructies om verbositeitsbias tegen te gaan (lengte niet belonen boven inhoud), confidentiebias (assertief taalgebruik niet belonen boven correcte voorzichtigheid), autoriteitsbias (jargon of aantal citaties niet belonen boven juistheid) en mildheidsbias (het volledige scorebereik van 1-6 gebruiken in plaats van in het midden te clusteren). Reviews worden neutraal gelabeld als \"Review A\" en \"Review B\" in plaats van \"referentie\" en \"gegenereerd\" om scoren op basis van herkomst te voorkomen.",
  compareJudgeSystemPromptLabel: "Systeemprompt",
  compareJudgeUserPromptLabel: "Gebruikersprompt (artikel + reviews tijdens runtime ingevoegd)",
  compareVsMid: " vs ",
  compareScoreOutOf: "/5",
  compareMetricCoverage: "Dekking",
  compareMetricSpecificity: "Specificiteit",
  compareMetricDepth: "Diepgang",
  compareJumpTo: "Spring naar",
  compareSectionOverallFeedback: "Algemene feedback",
  compareSectionDetailedComments: "Gedetailleerde opmerkingen",
  compareVisitPrefix: "Bezoek ",
  comparePdfReviewSuffix: " review",
  comparePdfFallback: "Download de PDF als de iframe niet weergeeft ↓",
};
