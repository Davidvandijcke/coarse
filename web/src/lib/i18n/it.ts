// Italian (it) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const it: Messages = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "Lingua del sito",

  // copy-to-clipboard code block
  codeBlockCopied: "copiato ✓",
  codeBlockCopy: "copia",

  // header
  headerTagline: "la revisione tra pari è un bene pubblico.",
  navSetup: "configurazione",
  navSideBySide: "confronto",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "Gli invii sono temporaneamente sospesi.",
  bannerBusyPrefix: "Il sistema è occupato (",
  bannerBusySuffix: " posti in uso). La tua revisione potrebbe essere messa in coda.",
  bannerFasterPrefix: "Per risultati più rapidi, prova la CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "Ehi ",
  heroGreetingSuffix: " puoi revisionare questo articolo?",
  heroHeading: "‘coarse!",
  heroLede:
    "Agenti IA revisionano il tuo articolo e scrivono un referto da revisore. Paghi direttamente i costi dell'API. Nessun account.",
  heroManifesto:
    "La revisione tra pari in ambito accademico si regge sul lavoro accademico non retribuito. Altri hanno deciso di farne un business. La cosa non ci è piaciuta.",

  // hero — score preview
  scoreVsOthers: "vs. altri revisori IA",
  statCostNum: "< $2*",
  statCostLabel: "per revisione",
  statCostFootnote: "*di solito :)",
  statCommentsNum: "20+",
  statCommentsLabel: "commenti dettagliati",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "open source",

  // hero — competitive comparison
  comparePrefix: "Valutato alla cieca rispetto a",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Ottiene punteggi più alti su copertura, specificità e profondità -- a una frazione del costo.",
  compareLink: "Guarda il confronto →",

  // submit form — section heading + paper field
  formSubmitHeading: "Invia un articolo",
  fieldPaper: "Articolo",
  dropzoneAriaLabel: "Carica il tuo articolo — trascina un file o clicca per sfogliare",
  dropzoneInputAriaLabel: "Scegli un file da caricare",
  dropzoneReplaceSuffix: " MB — clicca o trascina per sostituire",
  dropzonePromptPrefix: "Trascina qui il tuo file, oppure ",
  dropzoneBrowse: "sfoglia",
  dropzoneMaxSize: "Fino a 50 MB",

  // submit form — email field
  fieldEmail: "Email ",
  fieldEmailQualifier: "(solo per la revisione web)",
  emailPlaceholderUnavailable: "— non disponibile —",
  emailPlaceholder: "tu@universita.it",
  emailAriaLabel: "Indirizzo email",
  emailHelperDisabled:
    "La consegna delle email è temporaneamente sospesa. Salva la tua chiave di revisione al momento dell'invio e ricontrolla tra circa un'ora.",
  emailHelperPrefix:
    "Ti invieremo un'email quando sarà pronta. Controlla la cartella spam se non la vedi.",

  // submit form — OpenRouter key field
  fieldKey: "Chiave OpenRouter",
  fieldKeyGetOne: "ottienine una →",
  keyOrPaste: "— oppure incolla una chiave —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "Chiave API OpenRouter",
  keyHelper:
    "Le chiavi OAuth rimangono solo in questa scheda e si cancellano quando la chiudi. Non vengono mai salvate sui nostri server.",

  // submit form — author notes
  fieldNotes: "Note per il revisore",
  fieldNotesOptional: "(facoltativo)",
  notesPlaceholder:
    "es. concentrati sulla strategia di identificazione nel §3 — la sezione dati è ancora un segnaposto.",
  notesAriaLabel: "Note facoltative per orientare il revisore",
  notesHelper:
    "Orienta gli aspetti su cui si concentra il revisore. Non sovrascrive la rubrica di valutazione.",

  // submit form — cost estimate
  costEstimating: "Stima dei costi in corso...",
  costEstimatePrefix: "Costo API stimato: $",
  costUnavailable: "Stima dei costi non disponibile per questo modello",

  // submit form — Turnstile failure block
  turnstileFailedLine1Prefix:
    "Il nostro controllo umano non è andato a buon fine. Qualcosa sta bloccando o rallentando ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — di solito una modalità privacy rigorosa del browser (come la prevenzione del tracciamento di Safari o Firefox ETP in modalità rigorosa), un blocco di contenuti/pubblicità (Brave Shields, uBlock Origin con alcune liste), oppure una rete lenta o filtrata.",
  turnstileFailedLine2Prefix: "Prova prima a ricaricare la pagina. Se persiste, autorizza ",
  turnstileFailedLine2Mid: " per ",
  turnstileFailedLine2Suffix:
    " (disattiva i blocchi di contenuti o allenta le impostazioni sulla privacy), oppure usa un browser diverso. Su un URL di anteprima, il deployment potrebbe inoltre dover avere quel nome host nella lista di autorizzazione del widget Cloudflare Turnstile.",
  turnstileFailedLine3Prefix: "Oppure esegui coarse in locale con la tua chiave OpenRouter: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  // submit form — buttons + handoff picker
  submitButton: "Revisiona il mio articolo",
  submitButtonBusy: "Invio in corso...",
  submitOr: "oppure",
  handoffButton: "Revisiona con il mio abbonamento ▾",
  handoffButtonBusy: "Preparazione in corso...",

  // submit form — handoff progress messages
  handoffUploading: "Caricamento articolo...",
  handoffPreparing: "Preparazione del trasferimento...",

  // submit form — explanatory paragraphs
  explainReviewLabel: "Revisiona il mio articolo:",
  explainReviewBody:
    " OpenRouter gestisce tutto dall'inizio alla fine. Il file viene eliminato dopo l'elaborazione. La chiave di revisione funziona per 90 giorni. Di solito meno di $2.",
  explainSubscriptionLabel: "Revisiona con il mio abbonamento:",
  explainSubscriptionPart1:
    "ti diamo un comando shell che esegue l'intera pipeline coarse in locale usando il tuo abbonamento ",
  explainSubscriptionYour: "tuo",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", o",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "per il ragionamento dell'LLM.",
  explainSubscriptionPdf:
    "Paghi solo circa ~$0,10 per il passaggio locale di Mistral OCR (con la tua chiave OpenRouter); i caricamenti non PDF (.tex, .md, .docx, …) saltano l'OCR e non richiedono alcuna chiave OpenRouter.",
  explainSubscriptionNonPdf:
    "Il tuo file non è un PDF, quindi salta del tutto il passaggio di Mistral OCR — l'intera esecuzione è coperta dal tuo abbonamento, nessuna chiave OpenRouter necessaria.",
  explainSubscriptionPart3: "La revisione compare su questa pagina al termine.",
  explainDisclaimer:
    "Viene eseguito in locale sulla tua macchina usando il tuo account Claude Code, Codex o Gemini CLI. coarse.ink non riceve né conserva il login del tuo provider, e si applicano i termini, i limiti di utilizzo e le policy organizzative del tuo provider. coarse.ink non è affiliato ad Anthropic, OpenAI o Google.",

  // submit form — handoff result card
  handoffReviewWithPrefix: "Revisiona con ",
  handoffModelLabel: "modello",
  handoffEffortLabel: "impegno",
  handoffPastePromptPrefix: "Incolla questo prompt nel terminale di ",
  handoffPastePromptSuffix: ":",
  handoffRunHint:
    "L'agente aggiornerà la skill coarse-review, eseguirà l'intera revisione in locale e impiegherà 10–25 minuti. Il login del tuo provider rimane sulla tua macchina.",
  handoffKeyNeededPrefix:
    "La tua chiave OpenRouter deve prima trovarsi sulla tua macchina — esporta ",
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

  // retrieve
  findReviewHeading: "Trova una revisione",
  findReviewPlaceholder:
    "Incolla la tua chiave di revisione, il link completo della revisione o un vecchio ID di revisione...",
  findReviewAriaLabel: "Chiave di revisione",
  findReviewButton: "Trova",

  // footer
  footerPrivacy: "privacy",
  footerTerms: "termini",
  footerContact: "contatti",

  // status / errors (set in handlers)
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

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "Lingua della revisione",
  reviewLanguageAuto: "Automatica — segui la lingua dell'articolo",
  reviewLanguageHelper:
    "Per impostazione predefinita usa la lingua dell'articolo; le citazioni restano sempre nell'originale.",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "Modello",
  modelPickerUnavailableTitle: "Attualmente non disponibile",
  modelPickerSearchPlaceholder: "Cerca modelli...",
  modelPickerLoading: "Caricamento dei modelli...",
  modelPickerNoResults: "Nessun modello trovato.",
  modelPickerSearch: "cerca modelli...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "Connesso a OpenRouter",
  openRouterLogOut: "Disconnetti",
  openRouterLogIn: "Accedi con OpenRouter →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "Per questa revisione serve il link sicuro completo o la chiave di revisione.",
  statusLoadFailed: "Impossibile caricare lo stato della revisione. Riprova.",
  statusCancelledByUser: "Revisione annullata dall'utente",
  statusLoading: "Caricamento",
  statusAccessTokenRequired: "Token di accesso richiesto.",
  statusNotFoundHeading: "Revisione non trovata.",
  statusNotFoundBody: "Controlla la chiave di revisione e riprova.",
  statusCancelConfirmHeading: "Annullare la revisione?",
  statusCancelConfirmBody: "Sei sicuro? Non potrai vedere i tuoi risultati.",
  statusCancelling: "Annullamento in corso...",
  statusYesCancel: "Sì, annulla",
  statusGoBack: "Torna indietro",
  statusLabelCancelled: "annullata",
  statusLabelFailed: "non riuscita",
  statusLabelReviewing: "in revisione",
  statusLabelQueued: "in coda",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "Lettura del tuo articolo.",
  statusQueuedHeading: "In coda.",
  statusRunningBody: "Esecuzione della pipeline di revisione (di solito 30–60 minuti).",
  statusQueuedBody: "La tua revisione è in coda e inizierà a breve.",
  statusEmailWhenDone: "Ti invieremo un'email quando sarà pronta.",
  statusCancelledHeading: "Revisione annullata.",
  statusCancelledBody:
    "Il lavoro in coda è stato contrassegnato come annullato. Se l'elaborazione era già iniziata, il worker potrebbe impiegare un po' di tempo per fermarsi.",
  statusFailedHeading: "Non riuscita.",
  statusUnexpectedError: "Si è verificato un errore imprevisto.",
  statusResubmitPrefix: "Prova a inviare di nuovo, oppure segnala il tuo problema su ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: ".",
  statusTryAgain: "Riprova →",
  statusKeyBoxSave: "La tua chiave di revisione — conservala",
  statusKeyBoxLegacy: "Vecchio link di revisione",
  statusCopied: "Copiato",
  statusCopyLink: "Copia link",
  statusRedirectNote: "Questa pagina reindirizzerà automaticamente quando la tua revisione sarà pronta.",
  statusCancelReview: "Annulla revisione",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "Per questa revisione serve il link sicuro completo o la chiave di revisione.",
  reviewClientLoadFailed: "Impossibile caricare la revisione. Riprova.",
  reviewClientLoading: "Caricamento",
  reviewClientNotFoundHeading: "Revisione non trovata.",
  reviewClientNotFoundBody: "Controlla la tua chiave e riprova.",
  reviewClientSubmitNewPaper: "Invia un nuovo articolo →",
  reviewClientAccessTokenRequired: "Token di accesso richiesto.",
  reviewClientBackHome: "Torna alla home →",
  reviewClientReadingHeading: "Lettura del tuo articolo.",
  reviewClientQueuedHeading: "In coda.",
  reviewClientRunningBody: "Di solito 30–60 minuti. Questa pagina si aggiorna automaticamente.",
  reviewClientQueuedBody: "L'elaborazione inizia a breve.",
  reviewClientFailedHeading: "Revisione non riuscita.",
  reviewClientUnexpectedError: "Si è verificato un errore imprevisto.",
  reviewClientTryAgain: "Riprova →",
  reviewClientCancelledHeading: "Revisione annullata.",
  reviewClientCancelledBody: "Questa revisione è stata annullata prima del completamento.",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "Mostra meno",
  reviewShowMore: "Mostra altro",
  reviewShowInPaper: "Mostra nell'articolo",
  reviewMarkActive: "Segna come attivo",
  reviewMarkDone: "Segna come completato",
  reviewDismiss: "Ignora",
  reviewDiscuss: "Discuti",
  reviewDiscussTitle: "Discuti questo commento con un modello IA",
  reviewShowDetails: "Mostra dettagli",
  reviewStatusDone: "Completato",
  reviewStatusDismissed: "Ignorato",
  reviewHide: "Nascondi",
  reviewFilterAll: "Tutti",
  reviewFilterActive: "Attivi",
  reviewFilterDone: "Completati",
  reviewFilterDismissed: "Ignorati",
  reviewSidebarOverallFeedback: "Valutazione complessiva",
  reviewSidebarCommentsPrefix: "Commenti (",
  reviewSidebarCommentsRemainingSuffix: " rimanenti)",
  reviewRemainingSuffix: " rimanenti",
  reviewDownload: "Scarica",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "Stampa / PDF",
  reviewHidePaper: "Nascondi articolo",
  reviewShowPaper: "Mostra articolo",
  reviewCopied: "Copiato",
  reviewShare: "Condividi",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "Trascina per ridimensionare il pannello dell'articolo",
  reviewResizeTitle: "Trascina per ridimensionare",
  reviewOfPrefix: "Revisione di ",
  reviewMetaModel: "Modello",
  reviewMetaDate: "Data",
  reviewMetaDomain: "Ambito",
  reviewMetaTime: "Durata",
  reviewMetaCost: "Costo",
  reviewMetaReviewLanguage: "Lingua della revisione",
  reviewMetaAutoDetectedSuffix: " · rilevata automaticamente",
  reviewOverallFeedbackHeading: "Valutazione complessiva",
  reviewDetailedCommentsPrefix: "Commenti dettagliati (",
  reviewDetailedCommentsSuffix: ")",
  reviewGeneratedByPrefix: "Generato da ",
  reviewGeneratedBySuffix: ". Ovviamente.",
  reviewShareThisReview: "Condividi questa revisione",
  reviewDeleteReview: "Elimina revisione",
  reviewDeleteConfirmHeading: "Eliminare la revisione?",
  reviewDeleteConfirmBody: "Sei sicuro? Non potrai vedere i tuoi risultati.",
  reviewDeleting: "Eliminazione in corso...",
  reviewYesDelete: "Sì, elimina",
  reviewGoBack: "Torna indietro",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "Questa critica è davvero corretta?",
  chatExamplePrompt2: "Come dovrei rivedere il testo per tenerne conto?",
  chatExamplePrompt3: "In quale punto dell'articolo si applica?",
  chatNoResponse: "Nessuna risposta dal modello. Riprova o cambia modello.",
  chatSessionExpired: "La tua sessione OpenRouter è scaduta. Accedi di nuovo per continuare.",
  chatSomethingWrong: "Qualcosa è andato storto.",
  chatDiscussKicker: "Discuti · ",
  chatKickerComment: "commento n. ",
  chatKickerOverallFeedback: "valutazione complessiva",
  chatDiscussAriaPrefix: "Discuti: ",
  chatCloseAriaLabel: "Chiudi chat",
  chatDisconnectKeyTitle:
    "Disconnetti la tua chiave OpenRouter (non viene conservata oltre questa scheda)",
  chatDisconnectKey: "Disconnetti chiave",
  chatInputPlaceholder: "Chiedi informazioni su questo commento…",
  chatMessageAriaLabel: "Messaggio",
  chatStop: "Ferma",
  chatSend: "Invia",
  chatModelDisclosurePrefix: "Modello: ",
  chatKeyGateIntro:
    "Connetti OpenRouter per discutere di questo commento. La tua chiave viene inviata direttamente a OpenRouter — mai ai nostri server — e si cancella quando chiudi questa scheda.",
  chatKeyGateOrPaste: "— oppure incolla una chiave —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "Chiave API OpenRouter",
  chatKeyGateUseKey: "Usa la chiave",
  chatKeyGateHelper:
    "Le chiavi OAuth rimangono solo in questa scheda e si cancellano quando la chiudi. Non vengono mai salvate sui nostri server.",
  chatEmptyHintPrefix: "Chiedi qualsiasi cosa su questo commento. Ogni messaggio invia ",
  chatEmptyHintFullPaper: "l'intero articolo",
  chatEmptyHintQuotedPassage: "il passaggio citato e la valutazione",
  chatEmptyHintSuffix: " come contesto e consuma i tuoi crediti OpenRouter.",
  chatEmptyHintNoPaper:
    "Il testo completo dell'articolo non è conservato per questa revisione, quindi le risposte si basano solo sul passaggio citato e sulla valutazione.",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "Aperto ",
  handoffMenuOpenedPromptMid: " con il prompt precompilato — allega coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md, poi invia. (Il prompt è stato anche copiato, per sicurezza.)",
  handoffMenuOpenedPlainMid: " — allega coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md e incolla il prompt copiato.",
  handoffMenuButtonTitle:
    "Invia l'articolo + la revisione alla tua chat IA (Claude, ChatGPT, Gemini, Grok, DeepSeek)",
  handoffMenuButton: "Discuti con la tua IA",
  handoffMenuDownloadsIntro: "Scarica l'articolo + la revisione, poi apre:",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "Articolo",
  paperPanelDownload: "Scarica",
  paperPanelDownloadAriaLabel: "Scarica l'articolo in markdown",
  paperPanelCloseAriaLabel: "Chiudi il pannello dell'articolo",

  // setup page (setup/page.tsx)
  // setup page — tab switcher
  setupTablistAriaLabel: "Percorso di configurazione",
  setupTabOpenRouter: "Chiave OpenRouter",
  setupTabSubscription: "Usa il mio abbonamento",
  // setup page — OpenRouter tab intro
  setupOrHeading: "Ottieni la tua chiave OpenRouter",
  setupOrIntro:
    "Ci vogliono circa 2 minuti. Ti servirà una carta di credito per ~$1 di crediti iniziali — ricaricherai fino a $20 nel passaggio 2.",
  setupOrFasterLabel: "Opzione più rapida:",
  setupOrFasterMid1: " nel modulo principale puoi cliccare ",
  setupOrFasterLogIn: "“Accedi con OpenRouter”",
  setupOrFasterSuffix:
    " per autorizzare coarse e saltare la creazione manuale della chiave. Ti serve comunque un account OpenRouter con crediti (passaggi 1 e 2 qui sotto), e consigliamo comunque di impostare un limite di spesa per chiave (passaggio 4).",
  // setup page — OpenRouter step 1
  setupOrStep1Title: "Crea un account",
  setupOrStep1BodyPrefix: "Vai su ",
  setupOrStep1BodySuffix: " e clicca su “Get API Key” oppure registrati con Google / GitHub.",
  setupOrStep1Annotation: "homepage",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "Un'API unificata per gli LLM — una chiave, molti modelli.",
  // setup page — OpenRouter step 2
  setupOrStep2Title: "Aggiungi crediti",
  setupOrStep2BodyPrefix: "Vai su ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    ". Aggiungi almeno $20. I modelli open-source economici costano ~$0,25 a revisione; i modelli SOTA come Claude Opus o GPT-5 possono arrivare a $5–$10 su un articolo lungo. La stima dei costi mostrata prima dell'invio è indicativa, non un tetto massimo. Lascia un margine, altrimenti la revisione può esaurire la chiave a metà e fallire. I crediti non utilizzati non scadono.",
  setupOrStep2Annotation: "pagina dei crediti",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "Importo",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "Saldo: $0.00",
  // setup page — OpenRouter step 3
  setupOrStep3Title: "Crea una chiave API",
  setupOrStep3BodyPrefix: "Vai su ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: ", clicca su “Create Key” e chiamala ",
  setupOrStep3BodySuffix: ".",
  setupOrStep3Provisioning:
    "Assicurati che sia una normale chiave API — non una chiave di provisioning/gestione dalla sezione integrazioni. Le chiavi di provisioning possono creare ed elencare altre chiavi ma non possono eseguire inferenza, e coarse fallirà con “User not found” se ne incolli una.",
  setupOrStep3CopyWarning: "Copia la chiave ora — non la vedrai di nuovo.",
  setupOrStep3Annotation: "pagina delle chiavi",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "Nome chiave",
  setupOrStep3MockYourKey: "La tua chiave",
  // setup page — OpenRouter step 4
  setupOrStep4Title: "Imposta un limite di spesa sulla chiave",
  setupOrStep4BodyPrefix: "Nella ",
  setupOrStep4BodyLink: "pagina delle chiavi",
  setupOrStep4BodyMid1: ", clicca sul menu ",
  setupOrStep4BodyMid2: " accanto alla tua nuova chiave, scegli “Edit” e imposta il limite di credito ad ",
  setupOrStep4BodyAtLeast: "almeno $20",
  setupOrStep4BodySuffix:
    ". La chiave smette di funzionare una volta raggiunto il limite, quindi addebiti a sorpresa sono impossibili. Ma se lo imposti troppo stretto, una singola revisione costosa può esaurirlo a metà esecuzione.",
  setupOrStep4Annotation: "menu della chiave",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "Limite di credito per questa chiave",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "Perché è importante:",
  setupOrStep4WhyMid1: " coarse è open-source — puoi ",
  setupOrStep4WhyLink: "leggere ogni riga di codice",
  setupOrStep4WhySuffix:
    ". La tua chiave viene inviata direttamente a OpenRouter per eseguire la revisione, poi scartata — non viene mai conservata. Ma non devi fidarti di noi: il limite per chiave garantisce che non possa mai spendere più di quanto consenti, anche nel caso peggiore.",
  setupOrStep4CostLabel: "Una nota sulle stime dei costi:",
  setupOrStep4CostBody:
    " la stima mostrata prima dell'invio è un'euristica con un margine del ~15%, non un tetto massimo. Il costo effettivo sui modelli SOTA con articoli lunghi può arrivare fino a ~2× la stima una volta che entrano in gioco la verifica delle dimostrazioni e le riscritture della critica. Se il limite per chiave è impostato esattamente sulla stima, una revisione impegnativa può prosciugarlo e fallire a metà esecuzione. Lascia sempre un margine.",
  // setup page — OpenRouter step 5
  setupOrStep5Title: "Incolla in coarse",
  setupOrStep5Body: "Torna qui, incolla la tua chiave nel modulo e carica il tuo PDF.",
  setupOrStep5Annotation: "modulo coarse",
  setupOrStep5MockEmail: "Email",
  setupOrStep5MockKey: "Chiave OpenRouter",
  setupOrStep5MockButton: "Revisiona il mio articolo",
  // setup page — shared footer CTA
  setupReadyCta: "Pronto? Revisiona il tuo articolo →",
  // setup page — subscription tab intro
  setupSubHeading: "Usa l'abbonamento del tuo agente di coding",
  setupSubIntro1:
    "Per gli utenti che già pagano Claude Code, Codex o Gemini CLI. La revisione viene eseguita sul tuo abbonamento e viene addebitata lì. Paghi a OpenRouter solo ~$0,15 per il passaggio di OCR.",
  setupSubIntro2:
    "Viene eseguito in locale sulla tua macchina usando il tuo account Claude Code, Codex o Gemini CLI. coarse.ink non riceve né conserva il login del tuo provider. Si applicano comunque i termini e i limiti di utilizzo del tuo provider. coarse.ink non è affiliato ad Anthropic, OpenAI o Google.",
  // setup page — subscription step 1
  setupSubStep1Title: "Installa un agente di coding",
  setupSubStep1Body:
    "Scegli quello che paghi. Gemini CLI ha un piano gratuito se non ne hai uno. Installalo dalla pagina ufficiale del fornitore — la loro documentazione resta aggiornata.",
  setupSubStep1ClaudePrice: "Anthropic Pro o Max",
  setupSubStep1CodexPrice: "ChatGPT Plus, Pro o Business",
  setupSubStep1GeminiPrice: "Il piano gratuito va bene per la maggior parte degli articoli",
  setupSubStep1InstallLabel: "Istruzioni di installazione ↗",
  setupSubStep1Verify:
    "Esegui il comando di test per verificare installazione + login. Se stampa una risposta, sei a posto.",
  setupSubStep1CardLogin: "login: ",
  setupSubStep1CardTest: "test: ",
  // setup page — subscription step 2
  setupSubStep2Title: "Metti una chiave OpenRouter sulla tua macchina (solo PDF)",
  setupSubStep2BodyPrefix:
    "Questo passaggio si applica solo agli articoli in PDF — le fonti non PDF (.tex, .md, .docx, …) vengono estratte in locale senza OCR, quindi non richiedono alcuna chiave OpenRouter da nessuna parte e puoi passare direttamente al passaggio 3. Per i PDF, coarse ha comunque bisogno di OpenRouter per il passaggio di OCR (~$0,10 per articolo). Segui la scheda ",
  setupSubStep2BodyTab: "Chiave OpenRouter",
  setupSubStep2BodySuffix:
    " per creare un account, aggiungere $1 di credito e impostare un limite di $2 per chiave. Il margine di $20 del percorso solo OpenRouter non serve qui perché la revisione stessa viene eseguita sull'abbonamento del tuo agente di coding.",
  setupSubStep2KeyPrefix: "Poi metti la chiave sulla tua macchina: esegui ",
  setupSubStep2KeyMid1: ", inseriscila in un ",
  setupSubStep2KeyMid2: ", oppure salvala in ",
  setupSubStep2KeySuffix:
    ". La tua CLI la legge in locale quando esegue l'estrazione; coarse.ink non la vede mai.",
  // setup page — subscription step 3
  setupSubStep3Title: "Carica il tuo articolo e scegli una CLI",
  setupSubStep3BodyPrefix: "Nella ",
  setupSubStep3BodyLink: "pagina principale",
  setupSubStep3BodyMid: ", trascina il tuo articolo (PDF, .tex, .md, .docx, …) sul modulo, poi clicca sul menu a discesa ",
  setupSubStep3BodyButton: "Revisiona con il mio abbonamento ▾",
  setupSubStep3BodySuffix:
    " e scegli la tua CLI. coarse carica il file, genera un token di trasferimento e mostra il prompt che incollerai nel passaggio successivo. Qui non incolli la tua chiave OpenRouter nel modulo; la CLI la legge dalla tua macchina (passaggio 2).",
  // setup page — subscription step 4
  setupSubStep4Title: "Incolla il prompt nella tua CLI",
  setupSubStep4BodyPrefix: "coarse ti dà un unico prompt in linguaggio naturale. Copialo dal pannello, incollalo nella tua sessione ",
  setupSubStep4BodyMid1: ", ",
  setupSubStep4BodyMid2: " o ",
  setupSubStep4BodyMid3: " e premi invio. L'agente aggiorna il suo pacchetto di skill, esegue l'intera pipeline coarse con le proprie chiamate a sottoprocessi e stampa un ",
  setupSubStep4BodySuffix:
    " URL al termine. 10–25 minuti. Clicca sull'URL per aprire la revisione completata su coarse.ink.",
  setupSubStep4TimeoutLabel: "Se stai incollando in un agente di coding",
  setupSubStep4TimeoutSuffix:
    " (non un semplice terminale), aumenta il timeout dello strumento bash ad almeno 45 minuti prima di inviare il prompt. I timeout predefiniti degli agenti possono arrivare a soli 2 minuti, ben al di sotto del tempo di esecuzione di 10–25 minuti della revisione.",
  // setup page — subscription step 5 (troubleshooting)
  setupSubStep5Title: "Se qualcosa va storto",
  setupSubTrouble1Symptom: "Il pulsante “Try opening Claude Code / Codex” non fa nulla.",
  setupSubTrouble1Fix:
    "Il pulsante funziona solo se hai installato l'app desktop. Con un'installazione solo CLI, il browser non può avviare un terminale per te. Copia il prompt dal pannello e incollalo manualmente nella tua CLI.",
  setupSubTrouble2Symptom: "“No such command ‘install-skills’” durante l'esecuzione dell'agente.",
  setupSubTrouble2FixPrefix: "Si può ignorare. Il pacchetto di skill viene comunque caricato direttamente tramite ",
  setupSubTrouble2FixSuffix: "; l'agente proseguirà al passaggio di revisione.",
  setupSubTrouble3Symptom: "La mia fattura Anthropic / OpenAI / Google è aumentata dopo una revisione.",
  setupSubTrouble3FixPrefix: "Controlla la presenza di ",
  setupSubTrouble3FixMid1: ", ",
  setupSubTrouble3FixMid2: " o ",
  setupSubTrouble3FixSuffix:
    " nell'ambiente della tua shell. Se impostate, la CLI host addebita l'account API invece del tuo abbonamento. La v1.3.0+ le rimuove automaticamente, ma le versioni precedenti no.",
  setupSubTrouble4Symptom: "Meno commenti del solito (~10 invece di 15–25).",
  setupSubTrouble4FixPrefix: "Una sezione ha raggiunto il timeout di 30 minuti ed è stata scartata. Raro con l'impegno predefinito, più comune con ",
  setupSubTrouble4FixSuffix:
    " su articoli lunghi. Riesegui; abbassa l'impegno di un livello se succede due volte.",

  // compare page (ComparePage.tsx)
  comparePanelErrorBody: "Impossibile renderizzare questo elemento. Prova un altro modello o confronto.",
  comparePaperCorticalCircuits: "Circuiti corticali",
  comparePaperCosetCodes: "Codici coset",
  comparePaperPopulationGenetics: "Genetica delle popolazioni",
  comparePaperTargetingInterventions: "Targeting degli interventi",
  compareScoresShow: "Mostra",
  compareScoresHide: "Nascondi",
  compareScoresToggleSuffix: " tutti i punteggi tra gli articoli ",
  compareScoresColPaper: "Articolo",
  compareScoresColReference: "Riferimento",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "Valutato da Gemini 3.1 Pro con input multimodale PDF. 5.0/5 = corrisponde alla qualità di riferimento. 5.5+/5 = la supera.",
  compareJudgeShow: "Mostra",
  compareJudgeHide: "Nascondi",
  compareJudgeToggleSuffix: " il prompt del giudice inviato a Gemini 3.1 Pro ",
  compareJudgeExplain:
    "Per mitigare i noti bias del modello come giudice, il giudice viene eseguito due volte per ogni valutazione con le due revisioni invertite nell'ordine di presentazione, e i punteggi vengono mediati su entrambi gli ordinamenti. Questo contrasta il bias posizionale, per cui i giudici favoriscono sistematicamente la revisione che appare per prima. Il prompt include anche istruzioni specifiche per contrastare il bias di prolissità (non premiare la lunghezza rispetto alla sostanza), il bias di sicurezza (non premiare un linguaggio assertivo rispetto a un'opportuna cautela), il bias di autorità (non premiare il gergo o il numero di citazioni rispetto all'accuratezza) e il bias di indulgenza (usare l'intera scala di punteggio da 1 a 6 anziché concentrarsi nel mezzo). Le revisioni sono etichettate in modo neutro come \"Review A\" e \"Review B\" anziché \"riferimento\" e \"generata\" per evitare punteggi basati sulla provenienza.",
  compareJudgeSystemPromptLabel: "Prompt di sistema",
  compareJudgeUserPromptLabel: "Prompt utente (articolo + revisioni inseriti in fase di esecuzione)",
  compareVsMid: " vs ",
  compareScoreOutOf: "/5",
  compareMetricCoverage: "Copertura",
  compareMetricSpecificity: "Specificità",
  compareMetricDepth: "Profondità",
  compareJumpTo: "Vai a",
  compareSectionOverallFeedback: "Valutazione complessiva",
  compareSectionDetailedComments: "Commenti dettagliati",
  compareVisitPrefix: "Visita ",
  comparePdfReviewSuffix: " revisione",
  comparePdfFallback: "Scarica il PDF se l'iframe non viene renderizzato ↓",
};
