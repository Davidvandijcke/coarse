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

  scoreVsOthers: "évaluation ouverte",
  statCostNum: "< $2*",
  statCostLabel: "par évaluation",
  statCostFootnote: "*en général :)",
  statCommentsNum: "20+",
  statCommentsLabel: "commentaires détaillés",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "open source",

  comparePrefix: "Artefacts historiques côte à côte avec",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Illustratif uniquement — pas une preuve décisionnelle même modèle, ni un classement actuel.",
  compareLink: "Parcourir les comparaisons historiques →",

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
  notesHelper: "Indiquez au relecteur sur quoi se concentrer. Ne remplace pas la grille d'évaluation.",
  deepLiteratureLabel: "Recherche bibliographique approfondie",
  deepLiteratureHelper:
    "Utilise Perplexity Sonar Deep Research pour une recherche de sources plus exhaustive et en plusieurs étapes. Ajoute généralement quelques minutes et environ 0,30 $ à l'estimation.",
  deepLiteratureOn: "Activée",
  deepLiteratureOff: "Désactivée",

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
    "nous vous fournissons une commande shell qui exécute tout le pipeline coarse localement avec ",
  explainSubscriptionYour: "votre",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", ou",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "abonnement pour le raisonnement du LLM.",
  explainSubscriptionPdf:
    "Le traitement des PDF utilise votre clé OpenRouter pour l'OCR Mistral local et entraîne un léger coût de contrôle qualité visuel lorsque ce contrôle s'exécute ; les fichiers non PDF (.tex, .md, .docx, …) sautent l'OCR et n'ont besoin d'aucune clé OpenRouter.",
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

  // sélecteur de modèle (ModelPicker.tsx)
  modelPickerLabel: "Modèle",
  modelPickerUnavailableTitle: "Actuellement indisponible",
  modelPickerSearchPlaceholder: "Rechercher des modèles...",
  modelPickerLoading: "Chargement des modèles...",
  modelPickerNoResults: "Aucun modèle trouvé.",
  modelPickerSearch: "rechercher des modèles...",

  // bouton de connexion OpenRouter (OpenRouterLoginButton.tsx)
  openRouterConnected: "Connecté à OpenRouter",
  openRouterLogOut: "Se déconnecter",
  openRouterLogIn: "Se connecter avec OpenRouter →",

  // page de statut (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "Cette évaluation nécessite le lien d'évaluation sécurisé complet ou la clé d'évaluation.",
  statusLoadFailed: "Échec du chargement du statut de l'évaluation. Veuillez réessayer.",
  statusCancelledByUser: "Évaluation annulée par l'utilisateur",
  statusLoading: "Chargement",
  statusAccessTokenRequired: "Jeton d'accès requis.",
  statusNotFoundHeading: "Évaluation introuvable.",
  statusNotFoundBody: "Vérifiez la clé d'évaluation et réessayez.",
  statusCancelConfirmHeading: "Annuler l'évaluation ?",
  statusCancelConfirmBody: "Êtes-vous sûr ? Vous ne pourrez pas voir vos résultats.",
  statusCancelling: "Annulation...",
  statusYesCancel: "Oui, annuler",
  statusGoBack: "Retour",
  statusLabelCancelled: "annulée",
  statusLabelFailed: "échec",
  statusLabelReviewing: "évaluation en cours",
  statusLabelQueued: "en file d'attente",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "Lecture de votre article.",
  statusQueuedHeading: "En file d'attente.",
  statusRunningBody: "Exécution du pipeline d'évaluation (généralement 30–60 minutes).",
  statusQueuedBody: "Votre évaluation est en file d'attente et démarrera sous peu.",
  statusEmailWhenDone: "Nous vous enverrons un e-mail une fois terminé.",
  statusCancelledHeading: "Évaluation annulée.",
  statusCancelledBody:
    "La tâche en file d'attente a été marquée comme annulée. Si le travail avait déjà commencé, le worker peut prendre un peu de temps pour s'arrêter.",
  statusFailedHeading: "Échec.",
  statusUnexpectedError: "Une erreur inattendue s'est produite.",
  statusResubmitPrefix: "Veuillez réessayer de soumettre, ou signalez votre problème sur ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: ".",
  statusTryAgain: "Réessayer →",
  statusKeyBoxSave: "Votre clé d'évaluation — conservez-la",
  statusKeyBoxLegacy: "Ancien lien d'évaluation",
  statusCopied: "Copié",
  statusCopyLink: "Copier le lien",
  statusRedirectNote: "Cette page vous redirigera automatiquement une fois votre évaluation prête.",
  statusCancelReview: "Annuler l'évaluation",

  // chrome de la page d'évaluation (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "Cette évaluation nécessite le lien d'évaluation sécurisé complet ou la clé d'évaluation.",
  reviewClientLoadFailed: "Échec du chargement de l'évaluation. Veuillez réessayer.",
  reviewClientLoading: "Chargement",
  reviewClientNotFoundHeading: "Évaluation introuvable.",
  reviewClientNotFoundBody: "Vérifiez votre clé et réessayez.",
  reviewClientSubmitNewPaper: "Soumettre un nouvel article →",
  reviewClientAccessTokenRequired: "Jeton d'accès requis.",
  reviewClientBackHome: "Retour à l'accueil →",
  reviewClientReadingHeading: "Lecture de votre article.",
  reviewClientQueuedHeading: "En file d'attente.",
  reviewClientRunningBody: "Généralement 30–60 minutes. Cette page se met à jour automatiquement.",
  reviewClientQueuedBody: "Le traitement commence sous peu.",
  reviewClientFailedHeading: "Échec de l'évaluation.",
  reviewClientUnexpectedError: "Une erreur inattendue s'est produite.",
  reviewClientTryAgain: "Réessayer →",
  reviewClientCancelledHeading: "Évaluation annulée.",
  reviewClientCancelledBody: "Cette évaluation a été annulée avant d'être terminée.",

  // chrome de la page d'évaluation (ReviewDisplay.tsx)
  reviewShowLess: "Afficher moins",
  reviewShowMore: "Afficher plus",
  reviewShowInPaper: "Afficher dans l'article",
  reviewMarkActive: "Marquer comme actif",
  reviewMarkDone: "Marquer comme traité",
  reviewDismiss: "Ignorer",
  reviewDiscuss: "Discuter",
  reviewDiscussTitle: "Discuter de ce commentaire avec un modèle IA",
  reviewShowDetails: "Afficher les détails",
  reviewStatusDone: "Traité",
  reviewStatusDismissed: "Ignoré",
  reviewHide: "Masquer",
  reviewFilterAll: "Tous",
  reviewFilterActive: "Actifs",
  reviewFilterDone: "Traités",
  reviewFilterDismissed: "Ignorés",
  reviewSidebarOverallFeedback: "Retour global",
  reviewSidebarCommentsPrefix: "Commentaires (",
  reviewSidebarCommentsRemainingSuffix: " restants)",
  reviewRemainingSuffix: " restants",
  reviewDownload: "Télécharger",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "Imprimer / PDF",
  reviewHidePaper: "Masquer l'article",
  reviewShowPaper: "Afficher l'article",
  reviewCopied: "Copié",
  reviewShare: "Partager",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "Glisser pour redimensionner le panneau de l'article",
  reviewResizeTitle: "Glisser pour redimensionner",
  reviewOfPrefix: "Évaluation de ",
  reviewMetaModel: "Modèle",
  reviewMetaDate: "Date",
  reviewMetaDomain: "Domaine",
  reviewMetaTime: "Durée",
  reviewMetaCost: "Coût",
  reviewMetaReviewLanguage: "Langue de l'évaluation",
  reviewMetaAutoDetectedSuffix: " · détectée automatiquement",
  reviewOverallFeedbackHeading: "Retour global",
  reviewDetailedCommentsPrefix: "Commentaires détaillés (",
  reviewDetailedCommentsSuffix: ")",
  reviewGeneratedByPrefix: "Généré par ",
  reviewGeneratedBySuffix: ". Bien sûr.",
  reviewShareThisReview: "Partager cette évaluation",
  reviewDeleteReview: "Supprimer l'évaluation",
  reviewDeleteConfirmHeading: "Supprimer l'évaluation ?",
  reviewDeleteConfirmBody: "Êtes-vous sûr ? Vous ne pourrez pas voir vos résultats.",
  reviewDeleting: "Suppression...",
  reviewYesDelete: "Oui, supprimer",
  reviewGoBack: "Retour",

  // chrome de la page d'évaluation — chat de commentaire (CommentChat.tsx)
  chatExamplePrompt1: "Cette critique est-elle réellement correcte ?",
  chatExamplePrompt2: "Comment dois-je réviser pour y répondre ?",
  chatExamplePrompt3: "À quel endroit de l'article cela s'applique-t-il ?",
  chatNoResponse: "Aucune réponse du modèle. Réessayez ou changez de modèle.",
  chatSessionExpired: "Votre session OpenRouter a expiré. Reconnectez-vous pour continuer.",
  chatSomethingWrong: "Une erreur s'est produite.",
  chatDiscussKicker: "Discuter · ",
  chatKickerComment: "commentaire n°",
  chatKickerOverallFeedback: "retour global",
  chatDiscussAriaPrefix: "Discuter : ",
  chatCloseAriaLabel: "Fermer le chat",
  chatDisconnectKeyTitle:
    "Déconnecter votre clé OpenRouter (elle n'est pas conservée au-delà de cet onglet)",
  chatDisconnectKey: "Déconnecter la clé",
  chatInputPlaceholder: "Posez une question sur ce commentaire…",
  chatMessageAriaLabel: "Message",
  chatStop: "Arrêter",
  chatSend: "Envoyer",
  chatModelDisclosurePrefix: "Modèle : ",
  chatKeyGateIntro:
    "Connectez OpenRouter pour discuter de ce commentaire. Votre clé est envoyée directement à OpenRouter — jamais à nos serveurs — et est effacée lorsque vous fermez cet onglet.",
  chatKeyGateOrPaste: "— ou collez une clé —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "Clé API OpenRouter",
  chatKeyGateUseKey: "Utiliser la clé",
  chatKeyGateHelper:
    "Les clés OAuth restent uniquement dans cet onglet et sont effacées lorsque vous le fermez. Jamais enregistrées sur nos serveurs.",
  chatEmptyHintPrefix: "Posez n'importe quelle question sur ce commentaire. Chaque message envoie ",
  chatEmptyHintFullPaper: "l'article complet",
  chatEmptyHintQuotedPassage: "le passage cité et le retour",
  chatEmptyHintSuffix: " comme contexte et utilise vos crédits OpenRouter.",
  chatEmptyHintNoPaper:
    "Le texte complet de l'article n'est pas conservé pour cette évaluation, donc les réponses s'appuient uniquement sur le passage cité et le retour.",

  // chrome de la page d'évaluation — menu de transfert vers l'abonnement (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "Ouverture de ",
  handoffMenuOpenedPromptMid: " avec l'invite préremplie — joignez coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md, puis envoyez. (L'invite a aussi été copiée, au cas où.)",
  handoffMenuOpenedPlainMid: " — joignez coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md et collez l'invite copiée.",
  handoffMenuButtonTitle:
    "Envoyez l'article + l'évaluation à votre propre chat IA (Claude, ChatGPT, Gemini, Grok, DeepSeek)",
  handoffMenuButton: "Discuter avec votre IA",
  handoffMenuDownloadsIntro: "Télécharge l'article + l'évaluation, puis ouvre :",

  // chrome de la page d'évaluation — panneau de l'article (PaperPanel.tsx)
  paperPanelHeading: "Article",
  paperPanelDownload: "Télécharger",
  paperPanelDownloadAriaLabel: "Télécharger l'article en markdown",
  paperPanelCloseAriaLabel: "Fermer le panneau de l'article",

  // page de configuration (setup/page.tsx)
  // page de configuration — sélecteur d'onglets
  setupTablistAriaLabel: "Méthode de configuration",
  setupTabOpenRouter: "Clé OpenRouter",
  setupTabSubscription: "Utiliser mon abonnement",
  // page de configuration — introduction de l'onglet OpenRouter
  setupOrHeading: "Obtenez votre clé OpenRouter",
  setupOrIntro:
    "Cela prend environ 2 minutes. Vous aurez besoin d'une carte bancaire pour ~$1 de crédits afin de démarrer — vous compléterez jusqu'à $20 à l'étape 2.",
  setupOrFasterLabel: "Option plus rapide :",
  setupOrFasterMid1: " sur le formulaire principal, vous pouvez cliquer sur ",
  setupOrFasterLogIn: "« Se connecter avec OpenRouter »",
  setupOrFasterSuffix:
    " pour autoriser coarse et éviter la création manuelle de clé. Vous avez toujours besoin d'un compte OpenRouter avec des crédits (étapes 1 et 2 ci-dessous), et nous recommandons toujours de définir une limite de dépense par clé (étape 4).",
  // page de configuration — OpenRouter étape 1
  setupOrStep1Title: "Créez un compte",
  setupOrStep1BodyPrefix: "Rendez-vous sur ",
  setupOrStep1BodySuffix: " et cliquez sur « Get API Key » ou inscrivez-vous avec Google / GitHub.",
  setupOrStep1Annotation: "page d'accueil",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "Une API unifiée pour les LLM — une clé, plusieurs modèles.",
  // page de configuration — OpenRouter étape 2
  setupOrStep2Title: "Ajoutez des crédits",
  setupOrStep2BodyPrefix: "Accédez à ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    ". Ajoutez au moins $20. Les modèles open-source bon marché coûtent ~$0,25 par évaluation ; les modèles de pointe comme Claude Opus ou GPT-5 peuvent coûter $5–$10 sur un article long. L'estimation de coût affichée avant la soumission est un ordre de grandeur, pas un plafond. Laissez de la marge, sinon l'évaluation peut épuiser la clé à mi-parcours et échouer. Les crédits non utilisés n'expirent pas.",
  setupOrStep2Annotation: "page des crédits",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "Montant",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "Solde : $0.00",
  // page de configuration — OpenRouter étape 3
  setupOrStep3Title: "Créez une clé API",
  setupOrStep3BodyPrefix: "Rendez-vous sur ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: ", cliquez sur « Create Key », et nommez-la ",
  setupOrStep3BodySuffix: ".",
  setupOrStep3Provisioning:
    "Assurez-vous qu'il s'agit d'une clé API ordinaire — pas d'une clé de provisionnement/gestion de la section intégrations. Les clés de provisionnement peuvent créer et lister d'autres clés mais ne peuvent pas exécuter d'inférence, et coarse échouera avec « User not found » si vous en collez une.",
  setupOrStep3CopyWarning: "Copiez la clé maintenant — vous ne la reverrez plus.",
  setupOrStep3Annotation: "page des clés",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "Nom de la clé",
  setupOrStep3MockYourKey: "Votre clé",
  // page de configuration — OpenRouter étape 4
  setupOrStep4Title: "Définissez une limite de dépense sur la clé",
  setupOrStep4BodyPrefix: "Sur la ",
  setupOrStep4BodyLink: "page des clés",
  setupOrStep4BodyMid1: ", cliquez sur le menu ",
  setupOrStep4BodyMid2: " à côté de votre nouvelle clé, choisissez « Edit », et définissez la limite de crédit à ",
  setupOrStep4BodyAtLeast: "au moins $20",
  setupOrStep4BodySuffix:
    ". La clé cesse de fonctionner une fois la limite atteinte, donc les frais surprises sont impossibles. Mais si vous la fixez trop bas, une seule évaluation coûteuse peut l'épuiser en cours d'exécution.",
  setupOrStep4Annotation: "menu de la clé",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "Limite de crédit pour cette clé",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "Pourquoi c'est important :",
  setupOrStep4WhyMid1: " coarse est open-source — vous pouvez ",
  setupOrStep4WhyLink: "lire chaque ligne de code",
  setupOrStep4WhySuffix:
    ". Votre clé est envoyée directement à OpenRouter pour exécuter l'évaluation, puis supprimée — elle n'est jamais conservée. Mais vous n'avez pas à nous faire confiance : la limite par clé garantit qu'elle ne peut jamais dépenser plus que vous ne l'autorisez, même dans le pire des cas.",
  setupOrStep4CostLabel: "Une note sur les estimations de coût :",
  setupOrStep4CostBody:
    " l'estimation affichée avant la soumission est une heuristique avec une marge de ~15 %, pas un plafond strict. Le coût réel sur les modèles de pointe avec des articles longs peut atteindre ~2× l'estimation une fois que la vérification des preuves et les réécritures de critique entrent en jeu. Si le plafond par clé est exactement au niveau de l'estimation, une évaluation difficile peut l'épuiser et échouer en cours d'exécution. Laissez toujours de la marge.",
  // page de configuration — OpenRouter étape 5
  setupOrStep5Title: "Collez dans coarse",
  setupOrStep5Body: "Revenez ici, collez votre clé dans le formulaire et téléversez votre PDF.",
  setupOrStep5Annotation: "formulaire coarse",
  setupOrStep5MockEmail: "E-mail",
  setupOrStep5MockKey: "Clé OpenRouter",
  setupOrStep5MockButton: "Évaluer mon article",
  // page de configuration — appel à l'action partagé en bas de page
  setupReadyCta: "Prêt ? Évaluez votre article →",
  // page de configuration — introduction de l'onglet abonnement
  setupSubHeading: "Utilisez l'abonnement de votre agent de codage",
  setupSubIntro1:
    "Pour les utilisateurs qui paient déjà Claude Code, Codex ou Gemini CLI. L'évaluation s'exécute sur votre abonnement et y est facturée. Vous ne payez OpenRouter que pour l'OCR des PDF et tout contrôle qualité visuel déclenché.",
  setupSubIntro2:
    "S'exécute localement sur votre machine avec votre propre compte Claude Code, Codex ou Gemini CLI. coarse.ink ne reçoit ni ne conserve votre identifiant de connexion au fournisseur. Les conditions et limites d'utilisation de votre fournisseur s'appliquent toujours. coarse.ink n'est pas affilié à Anthropic, OpenAI ou Google.",
  // page de configuration — abonnement étape 1
  setupSubStep1Title: "Installez un agent de codage",
  setupSubStep1Body:
    "Choisissez celui que vous payez. Gemini CLI propose une offre gratuite si ce n'est pas le cas. Installez-le depuis la page du fournisseur — leur documentation reste à jour.",
  setupSubStep1ClaudePrice: "Anthropic Pro ou Max",
  setupSubStep1CodexPrice: "ChatGPT Plus, Pro ou Business",
  setupSubStep1GeminiPrice: "L'offre gratuite suffit pour la plupart des articles",
  setupSubStep1InstallLabel: "Instructions d'installation ↗",
  setupSubStep1Verify:
    "Exécutez la commande de test pour vérifier l'installation + la connexion. Si elle affiche une réponse, vous êtes prêt.",
  setupSubStep1CardLogin: "connexion : ",
  setupSubStep1CardTest: "test : ",
  // page de configuration — abonnement étape 2
  setupSubStep2Title: "Placez une clé OpenRouter sur votre machine (PDF uniquement)",
  setupSubStep2BodyPrefix:
    "Cette étape ne s'applique qu'aux articles PDF — les sources non PDF (.tex, .md, .docx, …) sont extraites localement sans OCR, donc elles n'ont besoin d'aucune clé OpenRouter nulle part et vous pouvez passer directement à l'étape 3. Pour les PDF, coarse a besoin d'OpenRouter pour l'OCR et tout contrôle qualité visuel déclenché. Suivez l'onglet ",
  setupSubStep2BodyTab: "Clé OpenRouter",
  setupSubStep2BodySuffix:
    " pour créer un compte, ajouter $1 de crédit et définir une limite de $2 par clé. La marge de $20 de la méthode OpenRouter seule n'est pas nécessaire ici, car l'évaluation elle-même s'exécute sur l'abonnement de votre agent de codage.",
  setupSubStep2KeyPrefix: "Placez ensuite la clé sur votre propre machine : exécutez ",
  setupSubStep2KeyMid1: ", déposez-la dans un ",
  setupSubStep2KeyMid2: ", ou enregistrez-la dans ",
  setupSubStep2KeySuffix:
    ". Votre CLI la lit localement lorsqu'elle exécute l'extraction ; coarse.ink ne la voit jamais.",
  // page de configuration — abonnement étape 3
  setupSubStep3Title: "Téléversez votre article et choisissez une CLI",
  setupSubStep3BodyPrefix: "Sur la ",
  setupSubStep3BodyLink: "page principale",
  setupSubStep3BodyMid: ", déposez votre article (PDF, .tex, .md, .docx, …) sur le formulaire, puis cliquez sur le menu déroulant ",
  setupSubStep3BodyButton: "Évaluer avec mon abonnement ▾",
  setupSubStep3BodySuffix:
    " et choisissez votre CLI. coarse téléverse le fichier, génère un jeton de transfert et affiche l'invite que vous collerez à l'étape suivante. Vous ne collez pas votre clé OpenRouter sur le formulaire ici ; la CLI la lit depuis votre machine (étape 2).",
  // page de configuration — abonnement étape 4
  setupSubStep4Title: "Collez l'invite dans votre CLI",
  setupSubStep4BodyPrefix: "coarse vous donne une invite en langage naturel. Copiez-la depuis le panneau, collez-la dans votre session ",
  setupSubStep4BodyMid1: ", ",
  setupSubStep4BodyMid2: ", ou ",
  setupSubStep4BodyMid3: ", et appuyez sur envoyer. L'agent actualise son lot de compétences, exécute tout le pipeline coarse via ses propres appels de sous-processus, et affiche une URL ",
  setupSubStep4BodySuffix:
    " une fois terminé. 10–25 minutes. Cliquez sur l'URL pour ouvrir l'évaluation terminée sur coarse.ink.",
  setupSubStep4TimeoutLabel: "Si vous collez dans un agent de codage",
  setupSubStep4TimeoutSuffix:
    " (et non un simple terminal), augmentez le délai d'expiration de son outil bash à au moins 45 min avant d'envoyer l'invite. Les délais par défaut des agents peuvent descendre jusqu'à 2 min, bien en deçà de la durée d'évaluation de 10–25 min.",
  // page de configuration — abonnement étape 5 (dépannage)
  setupSubStep5Title: "En cas de problème",
  setupSubTrouble1Symptom: "Le bouton « Essayer d'ouvrir Claude Code / Codex » ne fait rien.",
  setupSubTrouble1Fix:
    "Le bouton ne fonctionne que si l'application de bureau est installée. Avec une installation CLI uniquement, le navigateur ne peut pas lancer de terminal à votre place. Copiez l'invite depuis le panneau et collez-la manuellement dans votre CLI.",
  setupSubTrouble2Symptom: "« No such command 'install-skills' » pendant l'exécution de l'agent.",
  setupSubTrouble2FixPrefix: "Sans danger, à ignorer. Le lot de compétences se charge quand même directement via ",
  setupSubTrouble2FixSuffix: " ; l'agent passera à l'étape d'évaluation.",
  setupSubTrouble3Symptom: "Ma facture Anthropic / OpenAI / Google a augmenté après une évaluation.",
  setupSubTrouble3FixPrefix: "Vérifiez la présence de ",
  setupSubTrouble3FixMid1: ", ",
  setupSubTrouble3FixMid2: ", ou ",
  setupSubTrouble3FixSuffix:
    " dans l'environnement de votre shell. Si elle est définie, la CLI hôte facture le compte API au lieu de votre abonnement. La version v1.3.0+ les supprime automatiquement, mais les versions plus anciennes ne le faisaient pas.",
  setupSubTrouble4Symptom: "Moins de commentaires que d'habitude (~10 au lieu de 15–25).",
  setupSubTrouble4FixPrefix: "Une section a atteint le délai d'expiration de 30 min et a été abandonnée. Rare avec l'effort par défaut, plus fréquent avec ",
  setupSubTrouble4FixSuffix:
    " sur les articles longs. Relancez ; réduisez l'effort d'un cran si cela se produit deux fois.",

  // page de comparaison (ComparePage.tsx)
  comparePanelErrorBody: "Impossible d'afficher celle-ci. Essayez un autre modèle ou une autre comparaison.",
  comparePaperCorticalCircuits: "Circuits corticaux",
  comparePaperCosetCodes: "Codes de cosets",
  comparePaperPopulationGenetics: "Génétique des populations",
  comparePaperTargetingInterventions: "Ciblage des interventions",
  compareScoresShow: "Afficher",
  compareScoresHide: "Masquer",
  compareScoresToggleSuffix: " tous les scores pour tous les articles ",
  compareScoresColPaper: "Article",
  compareScoresColReference: "Référence",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "Scores historiques d’un juge LLM (Gemini 3.1 Pro, PDF multimodal). Échelle native 1–6 : 5,0 = égale la qualité de référence ; 5,5–6,0 = la dépasse. Ce n’est pas une preuve de classement à raisonnement maximal sur le même modèle.",
  compareJudgeShow: "Afficher",
  compareJudgeHide: "Masquer",
  compareJudgeToggleSuffix: " l'invite du juge envoyée à Gemini 3.1 Pro ",
  compareJudgeExplain:
    "Pour atténuer les biais connus du LLM-juge, le juge est exécuté deux fois par évaluation avec les deux relectures présentées dans un ordre inversé, et les scores sont moyennés sur les deux ordres. Cela contrecarre le biais de position, où les juges favorisent systématiquement la relecture présentée en premier. L'invite inclut aussi des instructions spécifiques pour contrecarrer le biais de verbosité (ne pas récompenser la longueur au détriment du fond), le biais de confiance (ne pas récompenser un ton affirmatif au détriment d'une prudence justifiée), le biais d'autorité (ne pas récompenser le jargon ou le nombre de citations au détriment de l'exactitude) et le biais de clémence (utiliser toute la plage de notation de 1 à 6 plutôt que de se regrouper au milieu). Les relectures sont étiquetées de façon neutre « Relecture A » et « Relecture B » plutôt que « référence » et « générée » afin d'éviter une notation fondée sur la provenance.",
  compareJudgeSystemPromptLabel: "Invite système",
  compareJudgeUserPromptLabel: "Invite utilisateur (article + relectures injectés à l'exécution)",
  compareVsMid: " vs ",
  compareScoreOutOf: "/6",
  compareMetricCoverage: "Couverture",
  compareMetricSpecificity: "Spécificité",
  compareMetricDepth: "Profondeur",
  compareJumpTo: "Aller à",
  compareSectionOverallFeedback: "Retour global",
  compareSectionDetailedComments: "Commentaires détaillés",
  compareVisitPrefix: "Visiter ",
  comparePdfReviewSuffix: " évaluation",
  comparePdfFallback: "Téléchargez le PDF si l'iframe ne s'affiche pas ↓",
  compareHistoricalBadge: "Exemple historique illustratif — pas une preuve de classement actuel",
  compareEvidenceUnavailable: "Preuve indisponible",
};
