// Spanish (es) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const es: Messages = {
  siteLanguageLabel: "Idioma del sitio",

  codeBlockCopied: "copiado ✓",
  codeBlockCopy: "copiar",

  headerTagline: "la revisión por pares es un bien público.",
  navSetup: "configuración",
  navSideBySide: "comparativa",
  navGithub: "github ↗",

  bannerPausedDefault: "Los envíos están pausados temporalmente.",
  bannerBusyPrefix: "El sistema está ocupado (",
  bannerBusySuffix: " espacios en uso). Tu revisión puede quedar en cola.",
  bannerFasterPrefix: "Para resultados más rápidos, prueba la CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "Oye ",
  heroGreetingSuffix: " ¿puedes revisar este artículo?",
  heroHeading: "‘coarse!",
  heroLede:
    "Agentes de IA revisan tu artículo y redactan un informe de árbitro. Pagas el coste de la API directamente. Sin cuenta.",
  heroManifesto:
    "La revisión académica por pares funciona con trabajo académico no remunerado. Otros decidieron hacer un negocio de eso. No nos gustó.",

  scoreVsOthers: "vs. otros revisores de IA",
  statCostNum: "< $2*",
  statCostLabel: "por revisión",
  statCostFootnote: "*normalmente :)",
  statCommentsNum: "20+",
  statCommentsLabel: "comentarios detallados",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "código abierto",

  comparePrefix: "Evaluado a ciegas frente a",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Puntúa más alto en cobertura, especificidad y profundidad -- a una fracción del coste.",
  compareLink: "Ver la comparativa →",

  formSubmitHeading: "Enviar un artículo",
  fieldPaper: "Artículo",
  dropzoneAriaLabel: "Sube tu artículo — arrastra un archivo o haz clic para explorar",
  dropzoneInputAriaLabel: "Elige un archivo para subir",
  dropzoneReplaceSuffix: " MB — haz clic o arrastra para reemplazar",
  dropzonePromptPrefix: "Arrastra tu archivo aquí, o ",
  dropzoneBrowse: "explora",
  dropzoneMaxSize: "Hasta 50 MB",

  fieldEmail: "Correo electrónico ",
  fieldEmailQualifier: "(solo para revisión web)",
  emailPlaceholderUnavailable: "— no disponible —",
  emailPlaceholder: "tu@universidad.edu",
  emailAriaLabel: "Dirección de correo electrónico",
  emailHelperDisabled:
    "El envío de correos está caído temporalmente. Guarda tu clave de revisión al enviar y vuelve dentro de aproximadamente una hora.",
  emailHelperPrefix:
    "Te enviaremos un correo cuando esté listo. Revisa tu carpeta de spam si no lo ves.",

  fieldKey: "Clave de OpenRouter",
  fieldKeyGetOne: "consigue una →",
  keyOrPaste: "— o pega una clave —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "Clave de API de OpenRouter",
  keyHelper:
    "Las claves OAuth permanecen solo en esta pestaña y se borran al cerrarla. Nunca se guardan en nuestros servidores.",

  fieldNotes: "Notas para el revisor",
  fieldNotesOptional: "(opcional)",
  notesPlaceholder:
    "p. ej. céntrate en la estrategia de identificación del §3 — la sección de datos todavía es un marcador de posición.",
  notesAriaLabel: "Notas opcionales para orientar al revisor",
  notesHelper: "Orienta en qué se centra el revisor. No anula la rúbrica.",

  costEstimating: "Estimando el coste...",
  costEstimatePrefix: "Coste estimado de la API: $",
  costUnavailable: "Estimación de coste no disponible para este modelo",

  turnstileFailedLine1Prefix:
    "Nuestra verificación humana no pudo completarse. Algo está bloqueando o ralentizando ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — normalmente un modo de privacidad estricto del navegador (como la prevención de rastreo de Safari o Firefox ETP estricto), un bloqueador de contenido/anuncios (Brave Shields, uBlock Origin en algunas listas), o una red lenta o filtrada.",
  turnstileFailedLine2Prefix: "Prueba primero a recargar la página. Si persiste, permite ",
  turnstileFailedLine2Mid: " para ",
  turnstileFailedLine2Suffix:
    " (desactiva los bloqueadores de contenido o relaja los ajustes de privacidad), o usa un navegador distinto. En una URL de vista previa, puede que la implementación también necesite ese nombre de host en la lista de permitidos del widget de Cloudflare Turnstile.",
  turnstileFailedLine3Prefix: "O ejecuta coarse en local con tu propia clave de OpenRouter: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  submitButton: "Revisar mi artículo",
  submitButtonBusy: "Enviando...",
  submitOr: "o",
  handoffButton: "Revisar con mi suscripción ▾",
  handoffButtonBusy: "Preparando...",

  handoffUploading: "Subiendo artículo...",
  handoffPreparing: "Preparando la transferencia...",

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
    "Solo pagas ~$0,10 por el paso local de Mistral OCR (con tu propia clave de OpenRouter); las subidas que no son PDF (.tex, .md, .docx, …) se saltan el OCR y no necesitan clave de OpenRouter.",
  explainSubscriptionNonPdf:
    "Tu archivo no es un PDF, así que se salta por completo el paso de Mistral OCR — toda la ejecución la cubre tu suscripción, sin necesidad de clave de OpenRouter.",
  explainSubscriptionPart3: "La revisión aparece en esta página cuando esté lista.",
  explainDisclaimer:
    "Se ejecuta en local en tu máquina usando tu propia cuenta de Claude Code, Codex o Gemini CLI. coarse.ink no recibe ni almacena el inicio de sesión de tu proveedor, y se aplican las condiciones, los límites de uso y las políticas de organización de tu proveedor. coarse.ink no está afiliado a Anthropic, OpenAI ni Google.",

  handoffReviewWithPrefix: "Revisar con ",
  handoffModelLabel: "modelo",
  handoffEffortLabel: "esfuerzo",
  handoffPastePromptPrefix: "Pega esta instrucción en tu terminal de ",
  handoffPastePromptSuffix: ":",
  handoffRunHint:
    "El agente actualizará la skill coarse-review, ejecutará toda la revisión en local y tardará entre 10–25 minutos. El inicio de sesión de tu proveedor permanece en tu máquina.",
  handoffKeyNeededPrefix:
    "Tu clave de OpenRouter debe estar primero en tu máquina — exporta ",
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

  findReviewHeading: "Buscar una revisión",
  findReviewPlaceholder: "Pega tu clave de revisión, el enlace completo de la revisión o el ID de revisión antiguo...",
  findReviewAriaLabel: "Clave de revisión",
  findReviewButton: "Buscar",

  footerPrivacy: "privacidad",
  footerTerms: "condiciones",
  footerContact: "contacto",

  noticeKeyMigrated:
    "Hemos movido tu clave de OpenRouter guardada a un almacenamiento exclusivo de esta pestaña. Se borrará cuando cierres esta pestaña.",
  errorLoginNoPersist:
    "Sesión iniciada, pero no se pudo conservar la clave en esta pestaña. Tendrás que pegarla de nuevo si esta página se recarga.",
  errorLoginFailed:
    "El inicio de sesión de OpenRouter falló. Inténtalo de nuevo o pega una clave manualmente.",
  errorAuthFailed:
    "La autenticación falló. En las implementaciones de vista previa esto suele significar que las credenciales de Basic Auth almacenadas en caché por el navegador no se enviaron al enviar el formulario. Actualiza la pestaña (Cmd/Ctrl+Shift+R), vuelve a iniciar sesión en el aviso de contraseña e inténtalo de nuevo.",
  errorServiceUnavailable: "Servicio no disponible temporalmente — inténtalo de nuevo en un minuto.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "Nuestro widget de verificación humana no pudo cargar — lo más probable es que una extensión del navegador (Brave Shields, uBlock Origin, Firefox ETP estricto) esté bloqueando challenges.cloudflare.com. Prueba a desactivarla para ",
  errorTurnstileBlockedSuffix: ", o ejecuta coarse en local: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "Todavía esperando a que cargue la verificación humana — dale un segundo e inténtalo de nuevo.",
  errorPrepareUpload: "No se pudo preparar la subida",
  errorUploadFailed: "La subida del archivo falló — inténtalo de nuevo",
  errorSubmissionFailed: "El envío falló",
  errorHandoffFailed: "La transferencia falló",
  launchCommandCopied: "Comando copiado al portapapeles. Pégalo en tu terminal.",
  launchOpeningCodex:
    "Abriendo la app de escritorio de Codex — el compositor debería rellenarse automáticamente. Pulsa enviar.",
  launchOpeningPrefix: "Abriendo ",
  launchOpeningSuffix: " — pega la instrucción desde tu portapapeles (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " la app de escritorio no se abrió. Si solo tienes instalada la versión CLI, pega los comandos de arriba en tu terminal.",
  errorLoginCouldNotStartPrefix: "El inicio de sesión de OpenRouter no pudo iniciarse: ",

  reviewLanguageLabel: "Idioma de la revisión",
  reviewLanguageAuto: "Automático — coincidir con el idioma del artículo",
  reviewLanguageHelper:
    "Por defecto, el propio idioma del artículo; las citas siempre permanecen en el original.",
};
