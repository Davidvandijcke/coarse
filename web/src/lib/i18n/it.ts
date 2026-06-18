// Italian (it) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const it: Messages = {
  siteLanguageLabel: "Lingua del sito",

  codeBlockCopied: "copiato ✓",
  codeBlockCopy: "copia",

  headerTagline: "la revisione paritaria è un bene pubblico.",
  navSetup: "configurazione",
  navSideBySide: "confronto",
  navGithub: "github ↗",

  bannerPausedDefault: "Gli invii sono temporaneamente sospesi.",
  bannerBusyPrefix: "Il sistema è occupato (",
  bannerBusySuffix: " posti in uso). La tua revisione potrebbe essere messa in coda.",
  bannerFasterPrefix: "Per risultati più rapidi, usa la CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "Ehi ",
  heroGreetingSuffix: " puoi revisionare questo articolo?",
  heroHeading: "‘coarse!",
  heroLede:
    "Gli agenti IA revisionano il tuo articolo e scrivono un referto da referee. Paghi i costi dell'API direttamente. Nessun account.",
  heroManifesto:
    "La revisione paritaria accademica si regge sul lavoro accademico non retribuito. Altri hanno deciso di farne un business. La cosa non ci è piaciuta.",

  scoreVsOthers: "vs. altri revisori IA",
  statCostNum: "< $2*",
  statCostLabel: "per revisione",
  statCostFootnote: "*di solito :)",
  statCommentsNum: "20+",
  statCommentsLabel: "commenti dettagliati",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "open source",

  comparePrefix: "Valutato alla cieca rispetto a",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Ottiene punteggi più alti su copertura, specificità e profondità -- a una frazione del costo.",
  compareLink: "Guarda il confronto →",

  formSubmitHeading: "Invia un articolo",
  fieldPaper: "Articolo",
  dropzoneAriaLabel: "Carica il tuo articolo — trascina un file o clicca per sfogliare",
  dropzoneInputAriaLabel: "Scegli un file da caricare",
  dropzoneReplaceSuffix: " MB — clicca o trascina per sostituire",
  dropzonePromptPrefix: "Trascina qui il tuo file, oppure ",
  dropzoneBrowse: "sfoglia",
  dropzoneMaxSize: "Fino a 50 MB",

  fieldEmail: "Email ",
  fieldEmailQualifier: "(solo per la revisione web)",
  emailPlaceholderUnavailable: "— non disponibile —",
  emailPlaceholder: "tu@universita.it",
  emailAriaLabel: "Indirizzo email",
  emailHelperDisabled:
    "La consegna delle email è temporaneamente sospesa. Salva la tua chiave di revisione al momento dell'invio e ricontrolla tra circa un'ora.",
  emailHelperPrefix:
    "Ti invieremo un'email quando sarà pronta. Controlla la cartella spam se non la vedi.",

  fieldKey: "Chiave OpenRouter",
  fieldKeyGetOne: "ottienine una →",
  keyOrPaste: "— oppure incolla una chiave —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "Chiave API OpenRouter",
  keyHelper:
    "Le chiavi OAuth rimangono solo in questa scheda e si cancellano quando la chiudi. Non vengono mai salvate sui nostri server.",

  fieldNotes: "Note per il revisore",
  fieldNotesOptional: "(facoltativo)",
  notesPlaceholder:
    "es. concentrati sulla strategia di identificazione nel §3 — la sezione dati è ancora un segnaposto.",
  notesAriaLabel: "Note facoltative per orientare il revisore",
  notesHelper: "Orienta gli aspetti su cui si concentra il revisore. Non sovrascrive la rubrica di valutazione.",

  costEstimating: "Stima dei costi in corso...",
  costEstimatePrefix: "Costo API stimato: $",
  costUnavailable: "Stima dei costi non disponibile per questo modello",

  turnstileFailedLine1Prefix:
    "Il nostro controllo umano non è andato a buon fine. Qualcosa sta bloccando o rallentando ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — di solito una modalità privacy rigorosa del browser (come la prevenzione del tracciamento di Safari o Firefox ETP rigoroso), un blocco contenuti/pubblicità (Brave Shields, uBlock Origin in alcune liste), oppure una rete lenta o filtrata.",
  turnstileFailedLine2Prefix: "Prova prima a ricaricare la pagina. Se persiste, autorizza ",
  turnstileFailedLine2Mid: " per ",
  turnstileFailedLine2Suffix:
    " (disattiva i blocchi contenuti o allenta le impostazioni sulla privacy), oppure usa un browser diverso. Su un URL di anteprima, il deployment potrebbe inoltre dover avere quel nome host nella lista di autorizzazione del widget Cloudflare Turnstile.",
  turnstileFailedLine3Prefix: "Oppure esegui coarse in locale con la tua chiave OpenRouter: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  submitButton: "Revisiona il mio articolo",
  submitButtonBusy: "Invio in corso...",
  submitOr: "oppure",
  handoffButton: "Revisiona con il mio abbonamento ▾",
  handoffButtonBusy: "Preparazione in corso...",

  handoffUploading: "Caricamento articolo...",
  handoffPreparing: "Preparazione del trasferimento...",

  explainReviewLabel: "Revisiona il mio articolo:",
  explainReviewBody:
    " OpenRouter gestisce tutto dall'inizio alla fine. Il file viene eliminato dopo l'elaborazione. La chiave di revisione funziona per 90 giorni. Di solito meno di $2.",
  explainSubscriptionLabel: "Revisiona con il mio abbonamento:",
  explainSubscriptionPart1:
    "ti diamo un comando shell che esegue l'intera pipeline coarse in locale usando ",
  explainSubscriptionYour: "il tuo",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", o",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "abbonamento per il ragionamento dell'LLM.",
  explainSubscriptionPdf:
    "Paghi solo circa ~$0,10 per il passaggio locale di Mistral OCR (con la tua chiave OpenRouter); i caricamenti non PDF (.tex, .md, .docx, …) saltano l'OCR e non richiedono alcuna chiave OpenRouter.",
  explainSubscriptionNonPdf:
    "Il tuo file non è un PDF, quindi salta del tutto il passaggio di Mistral OCR — l'intera esecuzione è coperta dal tuo abbonamento, nessuna chiave OpenRouter necessaria.",
  explainSubscriptionPart3: "La revisione compare su questa pagina al termine.",
  explainDisclaimer:
    "Viene eseguito in locale sulla tua macchina usando il tuo account Claude Code, Codex o Gemini CLI. coarse.ink non riceve né conserva il login del tuo provider, e si applicano i termini, i limiti di utilizzo e le policy organizzative del tuo provider. coarse.ink non è affiliato ad Anthropic, OpenAI o Google.",

  handoffReviewWithPrefix: "Revisiona con ",
  handoffModelLabel: "modello",
  handoffEffortLabel: "impegno",
  handoffPastePromptPrefix: "Incolla questo prompt nel terminale di ",
  handoffPastePromptSuffix: ":",
  handoffRunHint:
    "L'agente aggiornerà la skill coarse-review, eseguirà l'intera revisione in locale e impiegherà 10–25 minuti. Il login del tuo provider rimane sulla tua macchina.",
  handoffKeyNeededPrefix:
    "La tua chiave OpenRouter deve prima essere sulla tua macchina — esporta ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: ", oppure inseriscila in ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " o ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    ". Non la passiamo attraverso il browser perché l'URL di trasferimento finisce nel log della chat del tuo agente. Se manca, l'agente la chiederà.",
  handoffKeyNotNeeded:
    "Nessuna chiave OpenRouter necessaria per questo articolo — non è un PDF, quindi l'estrazione viene eseguita in locale senza il passaggio di Mistral OCR.",
  handoffReviewUrlIntro: "Quando la revisione sarà completata, comparirà all'indirizzo:",
  handoffInstallPrefix: "Non hai ancora ",
  handoffInstallSuffix: "? ",
  handoffInstallLink: "installalo →",

  findReviewHeading: "Trova una revisione",
  findReviewPlaceholder: "Incolla la tua chiave di revisione, il link completo della revisione o un vecchio ID di revisione...",
  findReviewAriaLabel: "Chiave di revisione",
  findReviewButton: "Trova",

  footerPrivacy: "privacy",
  footerTerms: "termini",
  footerContact: "contatti",

  noticeKeyMigrated:
    "Abbiamo spostato la tua chiave OpenRouter salvata in un'archiviazione valida solo per questa scheda. Si cancellerà quando chiuderai la scheda.",
  errorLoginNoPersist:
    "Accesso effettuato, ma non è stato possibile conservare la chiave in questa scheda. Dovrai incollarla di nuovo se la pagina si ricarica.",
  errorLoginFailed:
    "Login OpenRouter non riuscito. Riprova o incolla una chiave manualmente.",
  errorAuthFailed:
    "Autenticazione non riuscita. Sui deploy di anteprima questo di solito significa che le credenziali Basic Auth memorizzate nella cache del browser non sono state inviate all'invio del modulo. Aggiorna la scheda (Cmd/Ctrl+Shift+R), accedi di nuovo al prompt della password e riprova.",
  errorServiceUnavailable: "Servizio temporaneamente non disponibile — riprova tra un minuto.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "Il nostro widget di controllo umano non si è caricato — molto probabilmente un'estensione del browser (Brave Shields, uBlock Origin, Firefox ETP rigoroso) sta bloccando challenges.cloudflare.com. Prova a disattivarla per ",
  errorTurnstileBlockedSuffix: ", oppure esegui coarse in locale: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "Ancora in attesa del caricamento del controllo umano — dagli un secondo e riprova.",
  errorPrepareUpload: "Preparazione del caricamento non riuscita",
  errorUploadFailed: "Caricamento del file non riuscito — riprova",
  errorSubmissionFailed: "Invio non riuscito",
  errorHandoffFailed: "Trasferimento non riuscito",
  launchCommandCopied: "Comando copiato negli appunti. Incollalo nel tuo terminale.",
  launchOpeningCodex:
    "Apertura dell'app desktop Codex — il compositore dovrebbe precompilarsi. Premi invia.",
  launchOpeningPrefix: "Apertura di ",
  launchOpeningSuffix: " — incolla il prompt dai tuoi appunti (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " l'app desktop non si è aperta. Se hai installato solo la versione CLI, incolla invece i comandi qui sopra nel tuo terminale.",
  errorLoginCouldNotStartPrefix: "Il login OpenRouter non è riuscito ad avviarsi: ",

  reviewLanguageLabel: "Lingua della revisione",
  reviewLanguageAuto: "Automatica — segui la lingua dell'articolo",
  reviewLanguageHelper:
    "Per impostazione predefinita usa la lingua dell'articolo; le citazioni restano sempre nell'originale.",
};
