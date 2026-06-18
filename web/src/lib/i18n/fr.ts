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
    "Obtient de meilleurs scores en couverture, spécificité et profondeur -- pour une fraction du coût.",
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
  notesHelper: "Indiquez au relecteur sur quoi se concentrer. Ne remplace pas la grille d'évaluation.",

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
};
