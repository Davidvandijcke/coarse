// Arabic (ar) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Arabic is an RTL language — the site applies dir=rtl
// automatically when the Arabic UI is active, so values are plain translations
// without direction markers. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) render LTR within the RTL
// layout and are kept verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix
// fragments are significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const ar: Messages = {
  siteLanguageLabel: "لغة الموقع",

  codeBlockCopied: "تم النسخ ✓",
  codeBlockCopy: "نسخ",

  headerTagline: "مراجعة الأقران منفعة عامة.",
  navSetup: "الإعداد",
  navSideBySide: "مقارنة جنبًا إلى جنب",
  navGithub: "github ↗",

  bannerPausedDefault: "تم إيقاف الطلبات مؤقتًا.",
  bannerBusyPrefix: "النظام مشغول (",
  bannerBusySuffix: " مكانًا قيد الاستخدام). قد تُدرج مراجعتك في قائمة الانتظار.",
  bannerFasterPrefix: "للحصول على نتائج أسرع، جرّب واجهة سطر الأوامر:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "مرحبًا ",
  heroGreetingSuffix: " هل يمكنك مراجعة هذه الورقة؟",
  heroHeading: "‘coarse!",
  heroLede:
    "وكلاء الذكاء الاصطناعي يراجعون ورقتك ويكتبون تقرير تحكيم. تدفع تكلفة الـ API مباشرةً. بدون حساب.",
  heroManifesto:
    "تعتمد مراجعة الأقران الأكاديمية على عمل أكاديمي غير مدفوع الأجر. قرّر آخرون تحويل ذلك إلى تجارة. لم يعجبنا ذلك.",

  scoreVsOthers: "مقارنةً بمراجعي الذكاء الاصطناعي الآخرين",
  statCostNum: "< $2*",
  statCostLabel: "لكل مراجعة",
  statCostFootnote: "*عادةً :)",
  statCommentsNum: "20+",
  statCommentsLabel: "تعليقات مفصّلة",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "مفتوح المصدر",

  comparePrefix: "خضع لتقييم أعمى مقابل",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "يحقق درجات أعلى في الشمول والدقة والعمق -- بجزء بسيط من التكلفة.",
  compareLink: "اطّلع على المقارنة جنبًا إلى جنب →",

  formSubmitHeading: "أرسل ورقة",
  fieldPaper: "الورقة",
  dropzoneAriaLabel: "ارفع ورقتك — أفلت ملفًا أو انقر للتصفح",
  dropzoneInputAriaLabel: "اختر ملفًا للرفع",
  dropzoneReplaceSuffix: " ميغابايت — انقر أو أفلت للاستبدال",
  dropzonePromptPrefix: "أفلت ملفك هنا، أو ",
  dropzoneBrowse: "تصفّح",
  dropzoneMaxSize: "حتى 50 MB",

  fieldEmail: "البريد الإلكتروني ",
  fieldEmailQualifier: "(لمراجعة الويب فقط)",
  emailPlaceholderUnavailable: "— غير متاح —",
  emailPlaceholder: "you@university.edu",
  emailAriaLabel: "عنوان البريد الإلكتروني",
  emailHelperDisabled:
    "تسليم البريد الإلكتروني معطّل مؤقتًا. احفظ مفتاح المراجعة عند الإرسال وعد بعد ساعة تقريبًا.",
  emailHelperPrefix:
    "سنرسل إليك بريدًا إلكترونيًا عند الانتهاء. تحقّق من مجلد الرسائل غير المرغوب فيها إن لم تجده.",

  fieldKey: "مفتاح OpenRouter",
  fieldKeyGetOne: "احصل على واحد →",
  keyOrPaste: "— أو الصق مفتاحًا —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "مفتاح OpenRouter API",
  keyHelper:
    "تبقى مفاتيح OAuth في هذه التبويبة فقط وتُمحى عند إغلاقها. لا تُحفظ أبدًا على خوادمنا.",

  fieldNotes: "ملاحظات للمراجِع",
  fieldNotesOptional: "(اختياري)",
  notesPlaceholder:
    "مثال: يُرجى التركيز على استراتيجية التحديد في §3 — قسم البيانات ما زال عنصرًا نائبًا.",
  notesAriaLabel: "ملاحظات اختيارية لتوجيه المراجِع",
  notesHelper: "وجِّه ما يركّز عليه المراجِع. لا يتجاوز ذلك معايير التقييم.",

  costEstimating: "جارٍ تقدير التكلفة...",
  costEstimatePrefix: "تكلفة الـ API المقدّرة: $",
  costUnavailable: "تقدير التكلفة غير متاح لهذا النموذج",

  turnstileFailedLine1Prefix:
    "تعذّر إكمال فحص التحقق البشري. شيء ما يحجب أو يبطئ ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — عادةً وضع خصوصية صارم في المتصفح (مثل منع التتبع في Safari أو وضع Firefox ETP الصارم)، أو حاجب محتوى/إعلانات (Brave Shields، uBlock Origin في بعض القوائم)، أو شبكة بطيئة أو مُرشَّحة.",
  turnstileFailedLine2Prefix: "جرّب إعادة تحميل الصفحة أولًا. إذا استمرت المشكلة، اسمح لـ ",
  turnstileFailedLine2Mid: " من أجل ",
  turnstileFailedLine2Suffix:
    " (عطّل حواجب المحتوى أو خفّف إعدادات الخصوصية)، أو استخدم متصفحًا مختلفًا. على عنوان معاينة، قد يحتاج النشر أيضًا إلى إدراج اسم المضيف هذا في قائمة السماح لأداة Cloudflare Turnstile.",
  turnstileFailedLine3Prefix: "أو شغّل coarse محليًا بمفتاح OpenRouter الخاص بك: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  submitButton: "راجِع ورقتي",
  submitButtonBusy: "جارٍ الإرسال...",
  submitOr: "أو",
  handoffButton: "راجِع باستخدام اشتراكي ▾",
  handoffButtonBusy: "جارٍ التحضير...",

  handoffUploading: "جارٍ رفع الورقة...",
  handoffPreparing: "جارٍ تحضير التسليم...",

  explainReviewLabel: "راجِع ورقتي:",
  explainReviewBody:
    " يتولّى OpenRouter كل شيء من البداية إلى النهاية. يُحذف الملف بعد المعالجة. يعمل مفتاح المراجعة لمدة 90 يومًا. عادةً أقل من $2.",
  explainSubscriptionLabel: "راجِع باستخدام اشتراكي:",
  explainSubscriptionPart1:
    "نعطيك أمر صدفة (shell) يشغّل خط أنابيب coarse الكامل محليًا باستخدام ",
  explainSubscriptionYour: "اشتراكك",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: "،",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: "، أو",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "في استدلال الـ LLM.",
  explainSubscriptionPdf:
    "تدفع فقط نحو $0.10 لخطوة Mistral OCR المحلية (بمفتاح OpenRouter الخاص بك)؛ الملفات غير الـ PDF (.tex, .md, .docx, …) تتخطى الـ OCR ولا تحتاج إلى مفتاح OpenRouter.",
  explainSubscriptionNonPdf:
    "ملفك ليس PDF، لذا تُتخطى خطوة Mistral OCR بالكامل — يغطي اشتراكك التشغيل بأكمله، ولا حاجة إلى مفتاح OpenRouter.",
  explainSubscriptionPart3: "تظهر المراجعة على هذه الصفحة عند الانتهاء.",
  explainDisclaimer:
    "يعمل محليًا على جهازك باستخدام حسابك الخاص في Claude Code أو Codex أو Gemini CLI. لا يستلم coarse.ink بيانات تسجيل دخول مزوّدك ولا يخزّنها، وتسري شروط مزوّدك وحدود استخدامه وسياسات مؤسسته. coarse.ink غير تابع لـ Anthropic أو OpenAI أو Google.",

  handoffReviewWithPrefix: "راجِع باستخدام ",
  handoffModelLabel: "النموذج",
  handoffEffortLabel: "الجهد",
  handoffPastePromptPrefix: "الصق هذا الموجِّه في طرفية ",
  handoffPastePromptSuffix: " الخاصة بك:",
  handoffRunHint:
    "سيحدّث الوكيل مهارة coarse-review، ويشغّل المراجعة الكاملة محليًا، ويستغرق ذلك 10–25 دقيقة. تبقى بيانات تسجيل دخول مزوّدك على جهازك.",
  handoffKeyNeededPrefix:
    "يجب أن يكون مفتاح OpenRouter على جهازك أولًا — صدّر ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: "، أو ضعه في ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " أو ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    ". لا نمرّره عبر المتصفح لأن عنوان التسليم ينتهي في سجل محادثة وكيلك. إذا كان مفقودًا، سيطلبه الوكيل.",
  handoffKeyNotNeeded:
    "لا حاجة إلى مفتاح OpenRouter لهذه الورقة — فهي ليست PDF، لذا يعمل الاستخراج محليًا دون خطوة Mistral OCR.",
  handoffReviewUrlIntro: "عند انتهاء المراجعة، ستظهر على:",
  handoffInstallPrefix: "ألا تملك ",
  handoffInstallSuffix: " بعد؟ ",
  handoffInstallLink: "ثبّته →",

  findReviewHeading: "ابحث عن مراجعة",
  findReviewPlaceholder: "الصق مفتاح المراجعة أو رابط المراجعة الكامل أو معرّف المراجعة القديم...",
  findReviewAriaLabel: "مفتاح المراجعة",
  findReviewButton: "بحث",

  footerPrivacy: "الخصوصية",
  footerTerms: "الشروط",
  footerContact: "اتصل بنا",

  noticeKeyMigrated:
    "تم نقل مفتاح OpenRouter المحفوظ إلى تخزين خاص بهذه التبويبة فقط. سيُمحى عند إغلاق هذه التبويبة.",
  errorLoginNoPersist:
    "تم تسجيل الدخول، لكن تعذّر الاحتفاظ بالمفتاح في هذه التبويبة. ستحتاج إلى لصقه مرة أخرى إذا أُعيد تحميل هذه الصفحة.",
  errorLoginFailed:
    "فشل تسجيل الدخول إلى OpenRouter. يُرجى المحاولة مرة أخرى أو لصق مفتاح يدويًا.",
  errorAuthFailed:
    "فشلت المصادقة. على عمليات نشر المعاينة، يعني ذلك عادةً أن بيانات Basic Auth المخزّنة مؤقتًا في المتصفح لم تُرسَل عند تقديم النموذج. أعد تحميل التبويبة (Cmd/Ctrl+Shift+R)، وسجّل الدخول مرة أخرى عند مطالبة كلمة المرور، ثم أعد المحاولة.",
  errorServiceUnavailable: "الخدمة غير متاحة مؤقتًا — يُرجى المحاولة مرة أخرى بعد دقيقة.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "تعذّر تحميل أداة التحقق البشري لدينا — على الأرجح يحجب امتداد متصفح (Brave Shields، uBlock Origin، Firefox ETP الصارم) challenges.cloudflare.com. جرّب تعطيله من أجل ",
  errorTurnstileBlockedSuffix: "، أو شغّل coarse محليًا: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "لا يزال انتظار تحميل التحقق البشري جاريًا — امهله لحظة وحاول مرة أخرى.",
  errorPrepareUpload: "فشل تحضير الرفع",
  errorUploadFailed: "فشل رفع الملف — يُرجى المحاولة مرة أخرى",
  errorSubmissionFailed: "فشل الإرسال",
  errorHandoffFailed: "فشل التسليم",
  launchCommandCopied: "تم نسخ الأمر إلى الحافظة. الصقه في طرفيتك.",
  launchOpeningCodex:
    "جارٍ فتح تطبيق سطح المكتب Codex — يُفترض أن يُملأ المؤلِّف مسبقًا. اضغط على إرسال.",
  launchOpeningPrefix: "جارٍ فتح ",
  launchOpeningSuffix: " — الصق الموجِّه من حافظتك (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " لم يُفتح تطبيق سطح المكتب. إذا كنت تملك إصدار واجهة سطر الأوامر فقط، فالصق الأوامر أعلاه في طرفيتك بدلًا من ذلك.",
  errorLoginCouldNotStartPrefix: "تعذّر بدء تسجيل الدخول إلى OpenRouter: ",

  reviewLanguageLabel: "لغة المراجعة",
  reviewLanguageAuto: "تلقائي — مطابقة لغة الورقة",
  reviewLanguageHelper:
    "يُستخدم افتراضيًا لغة الورقة نفسها؛ تبقى الاقتباسات دائمًا بلغتها الأصلية.",
};
