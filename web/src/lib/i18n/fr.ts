// French (fr) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const fr: Messages = {
  siteLanguageLabel: "Langue du site",

  codeBlockCopied: "copié ✓",
  codeBlockCopy: "copier",

  headerTagline: "l'évaluation par les pairs est un bien public.",
  navSetup: "configuration",
  navSideBySide: "comparaison",
  navGithub: "github ↗",

  bannerPausedDefault: "Les soumissions sont temporairement suspendues.",
  bannerBusyPrefix: "Le système est saturé (",
  bannerBusySuffix: " emplacements utilisés). Votre évaluation sera peut-être mise en file d'attente.",
  bannerFasterPrefix: "Pour des résultats plus rapides, utilisez la CLI :",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "Salut ",
  heroGreetingSuffix: " peux-tu évaluer cet article ?",
  heroHeading: "‘coarse!",
  heroLede:
    "Des agents IA évaluent votre article et rédigent un rapport de relecture. Vous payez les coûts d'API directement. Sans compte.",
  heroManifesto:
    "L'évaluation académique par les pairs repose sur un travail universitaire non rémunéré. D'autres ont décidé d'en faire un commerce. Ça ne nous a pas plu.",

  scoreVsOthers: "vs. autres relecteurs IA",
  statCostNum: "< $2*",
  statCostLabel: "par évaluation",
  statCostFootnote: "*en général :)",
  statCommentsNum: "20+",
  statCommentsLabel: "commentaires détaillés",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "open source",

  comparePrefix: "Évalué à l'aveugle face à",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Obtient de meilleurs scores en couverture, précision et profondeur -- pour une fraction du coût.",
  compareLink: "Voir la comparaison →",

  formSubmitHeading: "Soumettre un article",
  fieldPaper: "Article",
  dropzoneAriaLabel: "Téléversez votre article — déposez un fichier ou cliquez pour parcourir",
  dropzoneInputAriaLabel: "Choisissez un fichier à téléverser",
  dropzoneReplaceSuffix: " Mo — cliquez ou déposez pour remplacer",
  dropzonePromptPrefix: "Déposez votre fichier ici, ou ",
  dropzoneBrowse: "parcourir",
  dropzoneMaxSize: "Jusqu'à 50 Mo",

  fieldEmail: "E-mail ",
  fieldEmailQualifier: "(uniquement pour l'évaluation web)",
  emailPlaceholderUnavailable: "— indisponible —",
  emailPlaceholder: "vous@universite.fr",
  emailAriaLabel: "Adresse e-mail",
  emailHelperDisabled:
    "La distribution des e-mails est temporairement hors service. Conservez votre clé d'évaluation au moment de la soumission et revenez dans environ une heure.",
  emailHelperPrefix:
    "Nous vous enverrons un e-mail une fois terminé. Vérifiez votre dossier de courrier indésirable si vous ne le voyez pas.",

  fieldKey: "Clé OpenRouter",
  fieldKeyGetOne: "en obtenir une →",
  keyOrPaste: "— ou collez une clé —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "Clé API OpenRouter",
  keyHelper:
    "Les clés OAuth restent uniquement dans cet onglet et sont effacées lorsque vous le fermez. Jamais enregistrées sur nos serveurs.",

  fieldNotes: "Notes pour le relecteur",
  fieldNotesOptional: "(facultatif)",
  notesPlaceholder:
    "p. ex. veuillez vous concentrer sur la stratégie d'identification au §3 — la section données est encore provisoire.",
  notesAriaLabel: "Notes facultatives pour orienter le relecteur",
  notesHelper: "Orientez ce sur quoi le relecteur se concentre. Ne remplace pas la grille d'évaluation.",

  costEstimating: "Estimation du coût...",
  costEstimatePrefix: "Coût d'API estimé : $",
  costUnavailable: "Estimation de coût indisponible pour ce modèle",

  turnstileFailedLine1Prefix:
    "Notre vérification humaine n'a pas pu aboutir. Quelque chose bloque ou ralentit ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — généralement un mode de confidentialité strict du navigateur (comme la prévention du suivi de Safari ou Firefox ETP strict), un bloqueur de contenu/publicités (Brave Shields, uBlock Origin sur certaines listes), ou un réseau lent ou filtré.",
  turnstileFailedLine2Prefix: "Essayez d'abord de recharger la page. Si cela persiste, autorisez ",
  turnstileFailedLine2Mid: " pour ",
  turnstileFailedLine2Suffix:
    " (désactivez les bloqueurs de contenu ou assouplissez les paramètres de confidentialité), ou utilisez un autre navigateur. Sur une URL de prévisualisation, le déploiement peut aussi nécessiter d'ajouter ce nom d'hôte à la liste d'autorisation du widget Cloudflare Turnstile.",
  turnstileFailedLine3Prefix: "Ou exécutez coarse localement avec votre propre clé OpenRouter : ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  submitButton: "Évaluer mon article",
  submitButtonBusy: "Soumission...",
  submitOr: "ou",
  handoffButton: "Évaluer avec mon abonnement ▾",
  handoffButtonBusy: "Préparation...",

  handoffUploading: "Téléversement de l'article...",
  handoffPreparing: "Préparation du transfert...",

  explainReviewLabel: "Évaluer mon article :",
  explainReviewBody:
    " OpenRouter gère tout de bout en bout. Le fichier est supprimé après traitement. La clé d'évaluation fonctionne pendant 90 jours. En général moins de $2.",
  explainSubscriptionLabel: "Évaluer avec mon abonnement :",
  explainSubscriptionPart1:
    "nous vous fournissons une commande shell qui exécute toute la pipeline coarse localement avec ",
  explainSubscriptionYour: "votre",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", ou",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "abonnement pour le raisonnement du LLM.",
  explainSubscriptionPdf:
    "Vous payez seulement ~$0,10 pour l'étape locale Mistral OCR (avec votre propre clé OpenRouter) ; les fichiers non PDF (.tex, .md, .docx, …) sautent l'OCR et n'ont besoin d'aucune clé OpenRouter.",
  explainSubscriptionNonPdf:
    "Votre fichier n'est pas un PDF, donc l'étape Mistral OCR est entièrement sautée — toute l'exécution est couverte par votre abonnement, aucune clé OpenRouter nécessaire.",
  explainSubscriptionPart3: "L'évaluation apparaît sur cette page une fois terminée.",
  explainDisclaimer:
    "S'exécute localement sur votre machine avec votre propre compte Claude Code, Codex ou Gemini CLI. coarse.ink ne reçoit ni ne conserve votre identifiant de connexion au fournisseur, et les conditions, limites d'utilisation et politiques d'organisation de votre fournisseur s'appliquent. coarse.ink n'est pas affilié à Anthropic, OpenAI ou Google.",

  handoffReviewWithPrefix: "Évaluer avec ",
  handoffModelLabel: "modèle",
  handoffEffortLabel: "effort",
  handoffPastePromptPrefix: "Collez cette invite dans votre terminal ",
  handoffPastePromptSuffix: " :",
  handoffRunHint:
    "L'agent actualisera la compétence coarse-review, exécutera toute l'évaluation localement et prendra 10–25 minutes. Votre identifiant de connexion au fournisseur reste sur votre machine.",
  handoffKeyNeededPrefix:
    "Votre clé OpenRouter doit d'abord se trouver sur votre machine — exportez ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: ", ou placez-la dans ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " ou ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    ". Nous ne la transmettons pas via le navigateur car l'URL de transfert finit dans le journal de conversation de votre agent. Si elle est absente, l'agent la demandera.",
  handoffKeyNotNeeded:
    "Aucune clé OpenRouter nécessaire pour cet article — ce n'est pas un PDF, donc l'extraction s'exécute localement sans l'étape Mistral OCR.",
  handoffReviewUrlIntro: "Une fois l'évaluation terminée, elle apparaîtra à :",
  handoffInstallPrefix: "Vous n'avez pas encore ",
  handoffInstallSuffix: " ? ",
  handoffInstallLink: "installez-le →",

  findReviewHeading: "Trouver une évaluation",
  findReviewPlaceholder: "Collez votre clé d'évaluation, le lien complet de l'évaluation ou l'ancien ID d'évaluation...",
  findReviewAriaLabel: "Clé d'évaluation",
  findReviewButton: "Trouver",

  footerPrivacy: "confidentialité",
  footerTerms: "conditions",
  footerContact: "contact",

  noticeKeyMigrated:
    "Votre clé OpenRouter enregistrée a été déplacée vers un stockage propre à cet onglet uniquement. Elle sera effacée lorsque vous fermerez cet onglet.",
  errorLoginNoPersist:
    "Connexion réussie, mais la clé n'a pas pu être conservée dans cet onglet. Vous devrez la recoller si cette page est rechargée.",
  errorLoginFailed:
    "Échec de la connexion à OpenRouter. Veuillez réessayer ou coller une clé manuellement.",
  errorAuthFailed:
    "Échec de l'authentification. Sur les déploiements de prévisualisation, cela signifie généralement que les identifiants Basic Auth mis en cache par le navigateur n'ont pas été envoyés lors de la soumission du formulaire. Actualisez l'onglet (Cmd/Ctrl+Maj+R), reconnectez-vous à l'invite de mot de passe et réessayez.",
  errorServiceUnavailable: "Service temporairement indisponible — veuillez réessayer dans une minute.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "Notre widget de vérification humaine n'a pas pu se charger — une extension de navigateur (Brave Shields, uBlock Origin, Firefox ETP strict) bloque très probablement challenges.cloudflare.com. Essayez de la désactiver pour ",
  errorTurnstileBlockedSuffix: ", ou exécutez coarse localement : uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "En attente du chargement de la vérification humaine — patientez une seconde et réessayez.",
  errorPrepareUpload: "Échec de la préparation du téléversement",
  errorUploadFailed: "Échec du téléversement du fichier — veuillez réessayer",
  errorSubmissionFailed: "Échec de la soumission",
  errorHandoffFailed: "Échec du transfert",
  launchCommandCopied: "Commande copiée dans le presse-papiers. Collez-la dans votre terminal.",
  launchOpeningCodex:
    "Ouverture de l'application de bureau Codex — le compositeur devrait être prérempli. Appuyez sur envoyer.",
  launchOpeningPrefix: "Ouverture de ",
  launchOpeningSuffix: " — collez l'invite depuis votre presse-papiers (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " l'application de bureau ne s'est pas ouverte. Si vous n'avez installé que la version CLI, collez plutôt les commandes ci-dessus dans votre terminal.",
  errorLoginCouldNotStartPrefix: "La connexion à OpenRouter n'a pas pu démarrer : ",

  reviewLanguageLabel: "Langue de l'évaluation",
  reviewLanguageAuto: "Automatique — suivre la langue de l'article",
  reviewLanguageHelper:
    "Par défaut, la langue propre de l'article ; les citations restent toujours dans la langue d'origine.",
};
