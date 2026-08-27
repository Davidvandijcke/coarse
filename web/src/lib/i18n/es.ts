// Spanish (es) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const es: Messages = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "Idioma del sitio",

  // copy-to-clipboard code block
  codeBlockCopied: "copiado ✓",
  codeBlockCopy: "copiar",

  // header
  headerTagline: "la revisión por pares es un bien público.",
  navSetup: "configuración",
  navSideBySide: "comparativa",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "Los envíos están pausados temporalmente.",
  bannerBusyPrefix: "El sistema está saturado (",
  bannerBusySuffix: " espacios en uso). Tu revisión podría quedar en cola.",
  bannerFasterPrefix: "Para obtener resultados más rápidos, prueba la CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "Oye ",
  heroGreetingSuffix: " ¿puedes revisar este artículo?",
  heroHeading: "‘coarse!",
  heroLede:
    "Agentes de IA revisan tu artículo y redactan un informe de árbitro. Pagas el coste de la API directamente. Sin cuenta.",
  heroManifesto:
    "La revisión académica por pares se sostiene sobre trabajo académico no remunerado. Otros decidieron hacer un negocio de eso. No nos pareció bien.",

  // hero — score preview
  scoreVsOthers: "frente a otros revisores de IA",
  statCostNum: "< $2*",
  statCostLabel: "por revisión",
  statCostFootnote: "*normalmente :)",
  statCommentsNum: "20+",
  statCommentsLabel: "comentarios detallados",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "código abierto",

  // hero — competitive comparison
  comparePrefix: "Evaluado a ciegas frente a",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Puntúa más alto en cobertura, especificidad y profundidad -- por una fracción del coste.",
  compareLink: "Ver la comparativa →",

  // submit form — section heading + paper field
  formSubmitHeading: "Enviar un artículo",
  fieldPaper: "Artículo",
  dropzoneAriaLabel: "Sube tu artículo — arrastra un archivo o haz clic para explorar",
  dropzoneInputAriaLabel: "Elige un archivo para subir",
  dropzoneReplaceSuffix: " MB — haz clic o arrastra para reemplazar",
  dropzonePromptPrefix: "Arrastra tu archivo aquí, o ",
  dropzoneBrowse: "explorar",
  dropzoneMaxSize: "Hasta 50 MB",

  // submit form — email field
  fieldEmail: "Correo electrónico ",
  fieldEmailQualifier: "(solo para la revisión web)",
  emailPlaceholderUnavailable: "— no disponible —",
  emailPlaceholder: "tu@universidad.edu",
  emailAriaLabel: "Dirección de correo electrónico",
  emailHelperDisabled:
    "El envío de correos está caído temporalmente. Guarda tu clave de revisión al enviar y vuelve a comprobarlo dentro de aproximadamente una hora.",
  emailHelperPrefix:
    "Te enviaremos un correo cuando esté lista. Revisa tu carpeta de spam si no lo ves.",

  // submit form — OpenRouter key field
  fieldKey: "Clave de OpenRouter",
  fieldKeyGetOne: "consigue una →",
  keyOrPaste: "— o pega una clave —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "Clave de API de OpenRouter",
  keyHelper:
    "Las claves OAuth permanecen solo en esta pestaña y se borran al cerrarla. Nunca se guardan en nuestros servidores.",

  // submit form — author notes
  fieldNotes: "Notas para el revisor",
  fieldNotesOptional: "(opcional)",
  notesPlaceholder:
    "p. ej. céntrate en la estrategia de identificación del §3 — la sección de datos todavía es un marcador de posición.",
  notesAriaLabel: "Notas opcionales para orientar al revisor",
  notesHelper: "Orienta en qué se centra el revisor. No anula la rúbrica.",
  deepLiteratureLabel: "Búsqueda bibliográfica profunda",
  deepLiteratureHelper:
    "Usa Perplexity Sonar Deep Research para una búsqueda de fuentes más exhaustiva y en varios pasos. Suele añadir unos minutos y alrededor de 0,30 USD a la estimación.",
  deepLiteratureOn: "Activada",
  deepLiteratureOff: "Desactivada",

  // submit form — cost estimate
  costEstimating: "Estimando el coste...",
  costEstimatePrefix: "Coste estimado de la API: $",
  costUnavailable: "Estimación de coste no disponible para este modelo",

  // submit form — Turnstile failure block
  turnstileFailedLine1Prefix:
    "Nuestra verificación humana no pudo completarse. Algo está bloqueando o ralentizando ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — normalmente un modo de privacidad estricto del navegador (como la prevención de rastreo de Safari o Firefox ETP en modo estricto), un bloqueador de contenido/anuncios (Brave Shields, uBlock Origin en algunas listas) o una red lenta o filtrada.",
  turnstileFailedLine2Prefix: "Prueba primero a recargar la página. Si persiste, permite ",
  turnstileFailedLine2Mid: " para ",
  turnstileFailedLine2Suffix:
    " (desactiva los bloqueadores de contenido o relaja los ajustes de privacidad), o usa otro navegador. En una URL de vista previa, puede que el despliegue también necesite ese nombre de host en la lista de permitidos del widget de Cloudflare Turnstile.",
  turnstileFailedLine3Prefix: "O ejecuta coarse en local con tu propia clave de OpenRouter: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  // submit form — buttons + handoff picker
  submitButton: "Revisar mi artículo",
  submitButtonBusy: "Enviando...",
  submitOr: "o",
  handoffButton: "Revisar con mi suscripción ▾",
  handoffButtonBusy: "Preparando...",

  // submit form — handoff progress messages
  handoffUploading: "Subiendo el artículo...",
  handoffPreparing: "Preparando la transferencia...",

  // submit form — explanatory paragraphs
  explainReviewLabel: "Revisar mi artículo:",
  explainReviewBody:
    " OpenRouter se encarga de todo de principio a fin. El archivo se elimina tras el procesamiento. La clave de revisión funciona durante 90 días. Normalmente menos de $2.",
  explainSubscriptionLabel: "Revisar con mi suscripción:",
  explainSubscriptionPart1:
    "te damos un comando de shell que ejecuta toda la pipeline de coarse en local usando tu suscripción de ",
  explainSubscriptionYour: "tu",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", o",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "para el razonamiento del LLM.",
  explainSubscriptionPdf:
    "El procesamiento de PDF usa tu clave de OpenRouter para el OCR local de Mistral y añade un pequeño cargo por QA visual cuando se ejecuta esa comprobación; las subidas que no son PDF (.tex, .md, .docx, …) se saltan el OCR y no necesitan clave de OpenRouter.",
  explainSubscriptionNonPdf:
    "Tu archivo no es un PDF, así que se salta por completo el paso de Mistral OCR — toda la ejecución la cubre tu suscripción, sin necesidad de clave de OpenRouter.",
  explainSubscriptionPart3: "La revisión aparece en esta página cuando termina.",
  explainDisclaimer:
    "Se ejecuta en local en tu máquina usando tu propia cuenta de Claude Code, Codex o Gemini CLI. coarse.ink no recibe ni almacena el inicio de sesión de tu proveedor, y se aplican las condiciones, los límites de uso y las políticas de organización de tu proveedor. coarse.ink no está afiliado a Anthropic, OpenAI ni Google.",

  // submit form — handoff result card
  handoffReviewWithPrefix: "Revisar con ",
  handoffModelLabel: "modelo",
  handoffEffortLabel: "esfuerzo",
  handoffPastePromptPrefix: "Pega esta instrucción en tu terminal de ",
  handoffPastePromptSuffix: ":",
  handoffRunHint:
    "El agente actualizará la skill coarse-review, ejecutará toda la revisión en local y tardará entre 10 y 25 minutos. El inicio de sesión de tu proveedor permanece en tu máquina.",
  handoffKeyNeededPrefix:
    "Tu clave de OpenRouter debe estar antes en tu máquina — exporta ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: ", o ponla en ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " o ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    ". No la pasamos a través del navegador porque la URL de transferencia acaba en el registro de chat de tu agente. Si falta, el agente la pedirá.",
  handoffKeyNotNeeded:
    "No se necesita clave de OpenRouter para este artículo — no es un PDF, así que la extracción se ejecuta en local sin el paso de Mistral OCR.",
  handoffReviewUrlIntro: "Cuando la revisión termine, aparecerá en:",
  handoffInstallPrefix: "¿No tienes ",
  handoffInstallSuffix: " todavía? ",
  handoffInstallLink: "instálalo →",

  // retrieve
  findReviewHeading: "Buscar una revisión",
  findReviewPlaceholder: "Pega tu clave de revisión, el enlace completo de la revisión o el ID de revisión antiguo...",
  findReviewAriaLabel: "Clave de revisión",
  findReviewButton: "Buscar",

  // footer
  footerPrivacy: "privacidad",
  footerTerms: "condiciones",
  footerContact: "contacto",

  // status / errors (set in handlers)
  noticeKeyMigrated:
    "Hemos movido tu clave de OpenRouter guardada a un almacenamiento exclusivo de esta pestaña. Se borrará cuando cierres esta pestaña.",
  errorLoginNoPersist:
    "Sesión iniciada, pero no se pudo conservar la clave en esta pestaña. Tendrás que pegarla de nuevo si esta página se recarga.",
  errorLoginFailed:
    "Falló el inicio de sesión de OpenRouter. Inténtalo de nuevo o pega una clave manualmente.",
  errorAuthFailed:
    "Falló la autenticación. En los despliegues de vista previa esto suele significar que las credenciales de Basic Auth almacenadas en la caché del navegador no se enviaron al enviar el formulario. Actualiza la pestaña (Cmd/Ctrl+Shift+R), vuelve a iniciar sesión en el aviso de contraseña e inténtalo de nuevo.",
  errorServiceUnavailable: "Servicio no disponible temporalmente — inténtalo de nuevo en un minuto.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "Nuestro widget de verificación humana no pudo cargarse — lo más probable es que una extensión del navegador (Brave Shields, uBlock Origin, Firefox ETP en modo estricto) esté bloqueando challenges.cloudflare.com. Prueba a desactivarla para ",
  errorTurnstileBlockedSuffix: ", o ejecuta coarse en local: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "Seguimos esperando a que cargue la verificación humana — dale un segundo e inténtalo de nuevo.",
  errorPrepareUpload: "No se pudo preparar la subida",
  errorUploadFailed: "Falló la subida del archivo — inténtalo de nuevo",
  errorSubmissionFailed: "Falló el envío",
  errorHandoffFailed: "Falló la transferencia",
  launchCommandCopied: "Comando copiado al portapapeles. Pégalo en tu terminal.",
  launchOpeningCodex:
    "Abriendo la app de escritorio de Codex — el editor debería rellenarse solo. Pulsa enviar.",
  launchOpeningPrefix: "Abriendo ",
  launchOpeningSuffix: " — pega la instrucción desde tu portapapeles (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " la app de escritorio no se abrió. Si solo tienes instalada la versión CLI, pega los comandos de arriba en tu terminal.",
  errorLoginCouldNotStartPrefix: "No se pudo iniciar el inicio de sesión de OpenRouter: ",

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "Idioma de la revisión",
  reviewLanguageAuto: "Automático — coincidir con el idioma del artículo",
  reviewLanguageHelper:
    "Por defecto, el propio idioma del artículo; las citas siempre permanecen en el original.",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "Modelo",
  modelPickerUnavailableTitle: "No disponible actualmente",
  modelPickerSearchPlaceholder: "Buscar modelos...",
  modelPickerLoading: "Cargando modelos...",
  modelPickerNoResults: "No se encontraron modelos.",
  modelPickerSearch: "buscar modelos...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "Conectado a OpenRouter",
  openRouterLogOut: "Cerrar sesión",
  openRouterLogIn: "Iniciar sesión con OpenRouter →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "Esta revisión requiere el enlace seguro completo de la revisión o la clave de revisión.",
  statusLoadFailed: "No se pudo cargar el estado de la revisión. Inténtalo de nuevo.",
  statusCancelledByUser: "Revisión cancelada por el usuario",
  statusLoading: "Cargando",
  statusAccessTokenRequired: "Se requiere un token de acceso.",
  statusNotFoundHeading: "Revisión no encontrada.",
  statusNotFoundBody: "Comprueba la clave de revisión e inténtalo de nuevo.",
  statusCancelConfirmHeading: "¿Cancelar la revisión?",
  statusCancelConfirmBody: "¿Estás seguro? No podrás ver tus resultados.",
  statusCancelling: "Cancelando...",
  statusYesCancel: "Sí, cancelar",
  statusGoBack: "Volver",
  statusLabelCancelled: "cancelada",
  statusLabelFailed: "fallida",
  statusLabelReviewing: "revisando",
  statusLabelQueued: "en cola",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "Leyendo tu artículo.",
  statusQueuedHeading: "En cola.",
  statusRunningBody: "Ejecutando la pipeline de revisión (normalmente entre 30 y 60 minutos).",
  statusQueuedBody: "Tu revisión está en cola y empezará en breve.",
  statusEmailWhenDone: "Te enviaremos un correo cuando esté lista.",
  statusCancelledHeading: "Revisión cancelada.",
  statusCancelledBody:
    "El trabajo en cola se marcó como cancelado. Si ya había comenzado, el worker puede tardar un poco en detenerse.",
  statusFailedHeading: "Fallida.",
  statusUnexpectedError: "Se produjo un error inesperado.",
  statusResubmitPrefix: "Vuelve a intentar el envío o publica tu problema en ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: ".",
  statusTryAgain: "Reintentar →",
  statusKeyBoxSave: "Tu clave de revisión — guárdala",
  statusKeyBoxLegacy: "Enlace de revisión antiguo",
  statusCopied: "Copiado",
  statusCopyLink: "Copiar enlace",
  statusRedirectNote: "Esta página redirigirá automáticamente cuando tu revisión esté lista.",
  statusCancelReview: "Cancelar la revisión",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "Esta revisión requiere el enlace seguro completo de la revisión o la clave de revisión.",
  reviewClientLoadFailed: "No se pudo cargar la revisión. Inténtalo de nuevo.",
  reviewClientLoading: "Cargando",
  reviewClientNotFoundHeading: "Revisión no encontrada.",
  reviewClientNotFoundBody: "Comprueba tu clave e inténtalo de nuevo.",
  reviewClientSubmitNewPaper: "Enviar un nuevo artículo →",
  reviewClientAccessTokenRequired: "Se requiere un token de acceso.",
  reviewClientBackHome: "Volver al inicio →",
  reviewClientReadingHeading: "Leyendo tu artículo.",
  reviewClientQueuedHeading: "En cola.",
  reviewClientRunningBody: "Normalmente entre 30 y 60 minutos. Esta página se actualiza automáticamente.",
  reviewClientQueuedBody: "El procesamiento empieza en breve.",
  reviewClientFailedHeading: "La revisión falló.",
  reviewClientUnexpectedError: "Se produjo un error inesperado.",
  reviewClientTryAgain: "Reintentar →",
  reviewClientCancelledHeading: "Revisión cancelada.",
  reviewClientCancelledBody: "Esta revisión se canceló antes de completarse.",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "Mostrar menos",
  reviewShowMore: "Mostrar más",
  reviewShowInPaper: "Mostrar en el artículo",
  reviewMarkActive: "Marcar como activo",
  reviewMarkDone: "Marcar como hecho",
  reviewDismiss: "Descartar",
  reviewDiscuss: "Debatir",
  reviewDiscussTitle: "Debate este comentario con un modelo de IA",
  reviewShowDetails: "Mostrar detalles",
  reviewStatusDone: "Hecho",
  reviewStatusDismissed: "Descartado",
  reviewHide: "Ocultar",
  reviewFilterAll: "Todos",
  reviewFilterActive: "Activos",
  reviewFilterDone: "Hechos",
  reviewFilterDismissed: "Descartados",
  reviewSidebarOverallFeedback: "Comentarios generales",
  reviewSidebarCommentsPrefix: "Comentarios (",
  reviewSidebarCommentsRemainingSuffix: " restantes)",
  reviewRemainingSuffix: " restantes",
  reviewDownload: "Descargar",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "Imprimir / PDF",
  reviewHidePaper: "Ocultar artículo",
  reviewShowPaper: "Mostrar artículo",
  reviewCopied: "Copiado",
  reviewShare: "Compartir",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "Arrastra para redimensionar el panel del artículo",
  reviewResizeTitle: "Arrastra para redimensionar",
  reviewOfPrefix: "Revisión de ",
  reviewMetaModel: "Modelo",
  reviewMetaDate: "Fecha",
  reviewMetaDomain: "Disciplina",
  reviewMetaTime: "Tiempo",
  reviewMetaCost: "Coste",
  reviewMetaReviewLanguage: "Idioma de la revisión",
  reviewMetaAutoDetectedSuffix: " · detectado automáticamente",
  reviewOverallFeedbackHeading: "Comentarios generales",
  reviewDetailedCommentsPrefix: "Comentarios detallados (",
  reviewDetailedCommentsSuffix: ")",
  reviewGeneratedByPrefix: "Generado por ",
  reviewGeneratedBySuffix: ". Por supuesto.",
  reviewShareThisReview: "Compartir esta revisión",
  reviewDeleteReview: "Eliminar la revisión",
  reviewDeleteConfirmHeading: "¿Eliminar la revisión?",
  reviewDeleteConfirmBody: "¿Estás seguro? No podrás ver tus resultados.",
  reviewDeleting: "Eliminando...",
  reviewYesDelete: "Sí, eliminar",
  reviewGoBack: "Volver",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "¿Es realmente correcta esta crítica?",
  chatExamplePrompt2: "¿Cómo debería revisar el artículo para abordarla?",
  chatExamplePrompt3: "¿En qué parte del artículo se aplica esto?",
  chatNoResponse: "Sin respuesta del modelo. Inténtalo de nuevo o cambia de modelo.",
  chatSessionExpired: "Tu sesión de OpenRouter caducó. Vuelve a iniciar sesión para continuar.",
  chatSomethingWrong: "Algo salió mal.",
  chatDiscussKicker: "Debatir · ",
  chatKickerComment: "comentario n.º ",
  chatKickerOverallFeedback: "comentarios generales",
  chatDiscussAriaPrefix: "Debatir: ",
  chatCloseAriaLabel: "Cerrar el chat",
  chatDisconnectKeyTitle:
    "Desconecta tu clave de OpenRouter (no se almacena más allá de esta pestaña)",
  chatDisconnectKey: "Desconectar clave",
  chatInputPlaceholder: "Pregunta sobre este comentario…",
  chatMessageAriaLabel: "Mensaje",
  chatStop: "Detener",
  chatSend: "Enviar",
  chatModelDisclosurePrefix: "Modelo: ",
  chatKeyGateIntro:
    "Conecta OpenRouter para debatir sobre este comentario. Tu clave se envía directamente a OpenRouter — nunca a nuestros servidores — y se borra cuando cierras esta pestaña.",
  chatKeyGateOrPaste: "— o pega una clave —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "Clave de API de OpenRouter",
  chatKeyGateUseKey: "Usar clave",
  chatKeyGateHelper:
    "Las claves OAuth permanecen solo en esta pestaña y se borran al cerrarla. Nunca se guardan en nuestros servidores.",
  chatEmptyHintPrefix: "Pregunta lo que quieras sobre este comentario. Cada mensaje envía ",
  chatEmptyHintFullPaper: "el artículo completo",
  chatEmptyHintQuotedPassage: "el pasaje citado y los comentarios",
  chatEmptyHintSuffix: " como contexto y se ejecuta con tus créditos de OpenRouter.",
  chatEmptyHintNoPaper:
    "El texto completo del artículo no se almacena para esta revisión, así que las respuestas se basan únicamente en el pasaje citado y los comentarios.",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "Se abrió ",
  handoffMenuOpenedPromptMid: " con la instrucción ya rellenada — adjunta coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md y envía. (La instrucción también se copió, por si acaso.)",
  handoffMenuOpenedPlainMid: " — adjunta coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md y pega la instrucción copiada.",
  handoffMenuButtonTitle:
    "Envía el artículo + la revisión a tu propio chat de IA (Claude, ChatGPT, Gemini, Grok, DeepSeek)",
  handoffMenuButton: "Debatir con tu IA",
  handoffMenuDownloadsIntro: "Descarga el artículo + la revisión y luego abre:",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "Artículo",
  paperPanelDownload: "Descargar",
  paperPanelDownloadAriaLabel: "Descargar el markdown del artículo",
  paperPanelCloseAriaLabel: "Cerrar el panel del artículo",

  // setup page (setup/page.tsx)
  // setup page — tab switcher
  setupTablistAriaLabel: "Ruta de configuración",
  setupTabOpenRouter: "Clave de OpenRouter",
  setupTabSubscription: "Usar mi suscripción",
  // setup page — OpenRouter tab intro
  setupOrHeading: "Consigue tu clave de OpenRouter",
  setupOrIntro:
    "Lleva unos 2 minutos. Necesitarás una tarjeta de crédito para ~$1 en créditos para empezar — añadirás hasta $20 en el paso 2.",
  setupOrFasterLabel: "Opción más rápida:",
  setupOrFasterMid1: " en el formulario principal puedes hacer clic en ",
  setupOrFasterLogIn: "“Iniciar sesión con OpenRouter”",
  setupOrFasterSuffix:
    " para autorizar a coarse y saltarte la creación manual de la clave. Aun así necesitas una cuenta de OpenRouter con créditos (pasos 1 y 2 más abajo), y seguimos recomendando establecer un límite de gasto por clave (paso 4).",
  // setup page — OpenRouter step 1
  setupOrStep1Title: "Crea una cuenta",
  setupOrStep1BodyPrefix: "Ve a ",
  setupOrStep1BodySuffix: " y haz clic en “Get API Key” o regístrate con Google / GitHub.",
  setupOrStep1Annotation: "página de inicio",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "Una API unificada para LLMs — una clave, muchos modelos.",
  // setup page — OpenRouter step 2
  setupOrStep2Title: "Añade créditos",
  setupOrStep2BodyPrefix: "Navega a ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    ". Añade al menos $20. Los modelos baratos de código abierto cuestan ~$0,25 por revisión; los modelos de última generación como Claude Opus o GPT-5 pueden costar entre $5 y $10 en un artículo largo. La estimación de coste que se muestra antes del envío es orientativa, no un tope. Deja margen o la revisión puede agotar la clave a la mitad y fallar. Los créditos no utilizados no caducan.",
  setupOrStep2Annotation: "página de créditos",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "Importe",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "Saldo: $0.00",
  // setup page — OpenRouter step 3
  setupOrStep3Title: "Crea una clave de API",
  setupOrStep3BodyPrefix: "Ve a ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: ", haz clic en “Create Key” y ponle el nombre ",
  setupOrStep3BodySuffix: ".",
  setupOrStep3Provisioning:
    "Asegúrate de que sea una clave de API normal — no una clave de aprovisionamiento/gestión de la sección de integraciones. Las claves de aprovisionamiento pueden crear y listar otras claves, pero no pueden ejecutar inferencia, y coarse fallará con “User not found” si pegas una.",
  setupOrStep3CopyWarning: "Copia la clave ahora — no volverás a verla.",
  setupOrStep3Annotation: "página de claves",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "Nombre de la clave",
  setupOrStep3MockYourKey: "Tu clave",
  // setup page — OpenRouter step 4
  setupOrStep4Title: "Establece un límite de gasto en la clave",
  setupOrStep4BodyPrefix: "En la ",
  setupOrStep4BodyLink: "página de claves",
  setupOrStep4BodyMid1: ", haz clic en el menú ",
  setupOrStep4BodyMid2: " junto a tu nueva clave, elige “Edit” y establece el límite de crédito en ",
  setupOrStep4BodyAtLeast: "al menos $20",
  setupOrStep4BodySuffix:
    ". La clave deja de funcionar una vez alcanzado el límite, así que los cargos sorpresa son imposibles. Pero si lo estableces demasiado ajustado, una sola revisión cara puede agotarlo a mitad de ejecución.",
  setupOrStep4Annotation: "menú de la clave",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "Límite de crédito para esta clave",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "Por qué esto importa:",
  setupOrStep4WhyMid1: " coarse es de código abierto — puedes ",
  setupOrStep4WhyLink: "leer cada línea de código",
  setupOrStep4WhySuffix:
    ". Tu clave se envía directamente a OpenRouter para ejecutar la revisión y luego se descarta — nunca se almacena. Pero no tienes que confiar en nosotros: el límite por clave garantiza que nunca pueda gastar más de lo que permitas, ni siquiera en el peor de los casos.",
  setupOrStep4CostLabel: "Una nota sobre las estimaciones de coste:",
  setupOrStep4CostBody:
    " la estimación que se muestra antes del envío es una heurística con un margen del ~15 %, no un tope rígido. El coste real en modelos de última generación con artículos largos puede llegar a ~2× la estimación una vez que entran en juego la verificación de pruebas y las reescrituras de la crítica. Si el tope por clave queda justo en la estimación, una revisión difícil puede vaciarlo y fallar a mitad de ejecución. Deja siempre margen.",
  // setup page — OpenRouter step 5
  setupOrStep5Title: "Pégala en coarse",
  setupOrStep5Body: "Vuelve aquí, pega tu clave en el formulario y sube tu PDF.",
  setupOrStep5Annotation: "formulario de coarse",
  setupOrStep5MockEmail: "Correo electrónico",
  setupOrStep5MockKey: "Clave de OpenRouter",
  setupOrStep5MockButton: "Revisar mi artículo",
  // setup page — shared footer CTA
  setupReadyCta: "¿Listo? Revisa tu artículo →",
  // setup page — subscription tab intro
  setupSubHeading: "Usa la suscripción de tu agente de programación",
  setupSubIntro1:
    "Para usuarios que ya pagan por Claude Code, Codex o Gemini CLI. La revisión se ejecuta en tu suscripción y se factura ahí. Solo pagas a OpenRouter por el OCR de los PDF y cualquier QA visual que se active.",
  setupSubIntro2:
    "Se ejecuta en local en tu máquina usando tu propia cuenta de Claude Code, Codex o Gemini CLI. coarse.ink no recibe ni almacena el inicio de sesión de tu proveedor. Se siguen aplicando las condiciones y los límites de uso de tu proveedor. coarse.ink no está afiliado a Anthropic, OpenAI ni Google.",
  // setup page — subscription step 1
  setupSubStep1Title: "Instala un agente de programación",
  setupSubStep1Body:
    "Elige el que pagues. Gemini CLI tiene un nivel gratuito si no pagas ninguno. Instálalo desde la propia página del proveedor — su documentación se mantiene al día.",
  setupSubStep1ClaudePrice: "Anthropic Pro o Max",
  setupSubStep1CodexPrice: "ChatGPT Plus, Pro o Business",
  setupSubStep1GeminiPrice: "El nivel gratuito sirve para la mayoría de los artículos",
  setupSubStep1InstallLabel: "Instrucciones de instalación ↗",
  setupSubStep1Verify:
    "Ejecuta el comando de prueba para verificar la instalación y el inicio de sesión. Si imprime una respuesta, ya está listo.",
  setupSubStep1CardLogin: "inicio de sesión: ",
  setupSubStep1CardTest: "prueba: ",
  // setup page — subscription step 2
  setupSubStep2Title: "Pon una clave de OpenRouter en tu máquina (solo PDFs)",
  setupSubStep2BodyPrefix:
    "Este paso solo se aplica a los artículos en PDF — las fuentes que no son PDF (.tex, .md, .docx, …) se extraen en local sin OCR, así que no necesitan ninguna clave de OpenRouter en ningún sitio y puedes saltar directamente al paso 3. Para los PDF, coarse necesita OpenRouter para el OCR y cualquier QA visual que se active. Sigue la pestaña ",
  setupSubStep2BodyTab: "Clave de OpenRouter",
  setupSubStep2BodySuffix:
    " para crear una cuenta, añadir $1 de crédito y establecer un límite de $2 por clave. El margen de $20 de la ruta exclusiva de OpenRouter no hace falta aquí porque la revisión en sí se ejecuta en la suscripción de tu agente de programación.",
  setupSubStep2KeyPrefix: "Luego pon la clave en tu propia máquina: ejecuta ",
  setupSubStep2KeyMid1: ", ponla en un ",
  setupSubStep2KeyMid2: ", o guárdala en ",
  setupSubStep2KeySuffix:
    ". Tu CLI la lee en local cuando ejecuta la extracción; coarse.ink nunca la ve.",
  // setup page — subscription step 3
  setupSubStep3Title: "Sube tu artículo y elige una CLI",
  setupSubStep3BodyPrefix: "En la ",
  setupSubStep3BodyLink: "página principal",
  setupSubStep3BodyMid: ", arrastra tu artículo (PDF, .tex, .md, .docx, …) al formulario y luego haz clic en el desplegable ",
  setupSubStep3BodyButton: "Revisar con mi suscripción ▾",
  setupSubStep3BodySuffix:
    " y elige tu CLI. coarse sube el archivo, acuña un token de transferencia y muestra la instrucción que pegarás en el siguiente paso. Aquí no pegas tu clave de OpenRouter en el formulario; la CLI la lee desde tu máquina (paso 2).",
  // setup page — subscription step 4
  setupSubStep4Title: "Pega la instrucción en tu CLI",
  setupSubStep4BodyPrefix: "coarse te da una sola instrucción en lenguaje natural. Cópiala del panel, pégala en tu sesión de ",
  setupSubStep4BodyMid1: ", ",
  setupSubStep4BodyMid2: ", o ",
  setupSubStep4BodyMid3: " y pulsa enviar. El agente actualiza su paquete de skills, ejecuta toda la pipeline de coarse en sus propias llamadas a subprocesos e imprime una URL de ",
  setupSubStep4BodySuffix:
    " cuando termina. De 10 a 25 minutos. Haz clic en la URL para abrir la revisión terminada en coarse.ink.",
  setupSubStep4TimeoutLabel: "Si vas a pegarla en un agente de programación",
  setupSubStep4TimeoutSuffix:
    " (no en una terminal normal), sube el tiempo de espera de su herramienta bash a al menos 45 min antes de enviar la instrucción. Los tiempos de espera por defecto de los agentes pueden ser de tan solo 2 min, muy por debajo del tiempo de ejecución de la revisión de 10 a 25 min.",
  // setup page — subscription step 5 (troubleshooting)
  setupSubStep5Title: "Si algo sale mal",
  setupSubTrouble1Symptom: "El botón “Intenta abrir Claude Code / Codex” no hace nada.",
  setupSubTrouble1Fix:
    "El botón solo funciona si tienes la app de escritorio instalada. Con una instalación solo de CLI, el navegador no puede abrirte una terminal. Copia la instrucción del panel y pégala en tu CLI manualmente.",
  setupSubTrouble2Symptom: "“No such command ‘install-skills’” dentro de la ejecución del agente.",
  setupSubTrouble2FixPrefix: "Se puede ignorar. El paquete de skills igualmente se carga directamente a través de ",
  setupSubTrouble2FixSuffix: "; el agente continuará con el paso de la revisión.",
  setupSubTrouble3Symptom: "Mi factura de Anthropic / OpenAI / Google subió tras una revisión.",
  setupSubTrouble3FixPrefix: "Comprueba si hay ",
  setupSubTrouble3FixMid1: ", ",
  setupSubTrouble3FixMid2: ", o ",
  setupSubTrouble3FixSuffix:
    " en el entorno de tu shell. Si están definidas, la CLI anfitriona factura a la cuenta de la API en lugar de a tu suscripción. v1.3.0+ las elimina automáticamente, pero las versiones anteriores no.",
  setupSubTrouble4Symptom: "Menos comentarios de lo habitual (~10 en lugar de 15–25).",
  setupSubTrouble4FixPrefix: "Una sección alcanzó el tiempo de espera de 30 min y se descartó. Es raro con el esfuerzo por defecto, más común con ",
  setupSubTrouble4FixSuffix:
    " en artículos largos. Vuelve a ejecutarla; baja el esfuerzo un nivel si ocurre dos veces.",

  // compare page (ComparePage.tsx)
  comparePanelErrorBody: "No se pudo renderizar este. Prueba con otro modelo o comparación.",
  comparePaperCorticalCircuits: "Circuitos Corticales",
  comparePaperCosetCodes: "Códigos de Clases Laterales",
  comparePaperPopulationGenetics: "Genética de Poblaciones",
  comparePaperTargetingInterventions: "Focalización de Intervenciones",
  compareScoresShow: "Mostrar",
  compareScoresHide: "Ocultar",
  compareScoresToggleSuffix: " todas las puntuaciones de los artículos ",
  compareScoresColPaper: "Artículo",
  compareScoresColReference: "Referencia",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "Evaluado por Gemini 3.1 Pro con entrada multimodal en PDF. 5,0/5 = iguala la calidad de la referencia. 5,5+/5 = la supera.",
  compareJudgeShow: "Mostrar",
  compareJudgeHide: "Ocultar",
  compareJudgeToggleSuffix: " la instrucción del juez enviada a Gemini 3.1 Pro ",
  compareJudgeExplain:
    "Para mitigar los sesgos conocidos del LLM como juez, el juez se ejecuta dos veces por evaluación con las dos revisiones intercambiadas en el orden de presentación, y las puntuaciones se promedian entre ambos órdenes. Esto contrarresta el sesgo posicional, por el que los jueces favorecen sistemáticamente la revisión que aparece primero. La instrucción también incluye indicaciones específicas para contrarrestar el sesgo de verbosidad (no premiar la extensión por encima de la sustancia), el sesgo de confianza (no premiar el lenguaje categórico por encima de la cautela correcta), el sesgo de autoridad (no premiar la jerga ni el número de citas por encima de la exactitud) y el sesgo de indulgencia (usar todo el rango de puntuación del 1 al 6 en lugar de agruparse en el centro). Las revisiones se etiquetan de forma neutra como \"Revisión A\" y \"Revisión B\" en lugar de \"referencia\" y \"generada\" para evitar puntuar en función de la procedencia.",
  compareJudgeSystemPromptLabel: "Instrucción del sistema",
  compareJudgeUserPromptLabel: "Instrucción del usuario (el artículo y las revisiones se inyectan en tiempo de ejecución)",
  compareVsMid: " frente a ",
  compareScoreOutOf: "/5",
  compareMetricCoverage: "Cobertura",
  compareMetricSpecificity: "Especificidad",
  compareMetricDepth: "Profundidad",
  compareJumpTo: "Saltar a",
  compareSectionOverallFeedback: "Comentarios generales",
  compareSectionDetailedComments: "Comentarios detallados",
  compareVisitPrefix: "Visita ",
  comparePdfReviewSuffix: " revisión",
  comparePdfFallback: "Descarga el PDF si el iframe no se renderiza ↓",
};
