// Arabic (ar) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Arabic is an RTL language — the site applies dir=rtl
// automatically when the Arabic UI is active, so values are plain translations
// without direction markers. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) render LTR within the RTL
// layout and are kept verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix
// fragments are significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const ar: Messages = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "لغة الموقع",

  // copy-to-clipboard code block
  codeBlockCopied: "تم النسخ ✓",
  codeBlockCopy: "نسخ",

  // header
  headerTagline: "مراجعة الأقران منفعة عامة.",
  navSetup: "الإعداد",
  navSideBySide: "مقارنة جنبًا إلى جنب",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "تم إيقاف الطلبات مؤقتًا.",
  bannerBusyPrefix: "النظام مشغول (",
  bannerBusySuffix: " مكانًا قيد الاستخدام). قد تُدرَج مراجعتك في قائمة الانتظار.",
  bannerFasterPrefix: "للحصول على نتائج أسرع، جرِّب واجهة سطر الأوامر:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "مرحبًا ",
  heroGreetingSuffix: " هل يمكنك مراجعة هذه الورقة؟",
  heroHeading: "‘coarse!",
  heroLede:
    "وكلاء ذكاء اصطناعي يراجعون ورقتك ويكتبون تقرير تحكيم. تدفع تكلفة الـ API مباشرةً. دون حساب.",
  heroManifesto:
    "تقوم مراجعة الأقران الأكاديمية على عمل أكاديمي غير مدفوع الأجر. وقد قرّر آخرون أن يجعلوا منها تجارة. لم يرُقْ لنا ذلك.",

  // hero — score preview
  scoreVsOthers: "مقارنةً بمراجِعي الذكاء الاصطناعي الآخرين",
  statCostNum: "< $2*",
  statCostLabel: "لكل مراجعة",
  statCostFootnote: "*عادةً :)",
  statCommentsNum: "20+",
  statCommentsLabel: "تعليقات مفصّلة",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "مفتوح المصدر",

  // hero — competitive comparison
  comparePrefix: "خضع لتقييم أعمى مقابل",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "يحقّق درجات أعلى في الشمول والدقة والعمق -- بجزء يسير من التكلفة.",
  compareLink: "اطّلع على المقارنة جنبًا إلى جنب →",

  // submit form — section heading + paper field
  formSubmitHeading: "أرسِل ورقة",
  fieldPaper: "الورقة",
  dropzoneAriaLabel: "ارفع ورقتك — أفلِت ملفًا أو انقر للتصفح",
  dropzoneInputAriaLabel: "اختر ملفًا للرفع",
  dropzoneReplaceSuffix: " ميغابايت — انقر أو أفلِت للاستبدال",
  dropzonePromptPrefix: "أفلِت ملفك هنا، أو ",
  dropzoneBrowse: "تصفّح",
  dropzoneMaxSize: "حتى 50 MB",

  // submit form — email field
  fieldEmail: "البريد الإلكتروني ",
  fieldEmailQualifier: "(لمراجعة الويب فقط)",
  emailPlaceholderUnavailable: "— غير متاح —",
  emailPlaceholder: "you@university.edu",
  emailAriaLabel: "عنوان البريد الإلكتروني",
  emailHelperDisabled:
    "تسليم البريد الإلكتروني معطّل مؤقتًا. احفظ مفتاح المراجعة عند الإرسال وعُد بعد ساعة تقريبًا.",
  emailHelperPrefix:
    "سنرسل إليك بريدًا إلكترونيًا عند الانتهاء. تحقّق من مجلد الرسائل غير المرغوب فيها إن لم تجده.",

  // submit form — OpenRouter key field
  fieldKey: "مفتاح OpenRouter",
  fieldKeyGetOne: "احصل على واحد →",
  keyOrPaste: "— أو الصق مفتاحًا —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "مفتاح OpenRouter API",
  keyHelper:
    "تبقى مفاتيح OAuth في هذه التبويبة فقط وتُمحى عند إغلاقها. ولا تُحفظ أبدًا على خوادمنا.",

  // submit form — author notes
  fieldNotes: "ملاحظات للمراجِع",
  fieldNotesOptional: "(اختياري)",
  notesPlaceholder:
    "مثال: يُرجى التركيز على استراتيجية التحديد في §3 — قسم البيانات ما زال عنصرًا نائبًا.",
  notesAriaLabel: "ملاحظات اختيارية لتوجيه المراجِع",
  notesHelper: "وجِّه ما يركّز عليه المراجِع. لا يتجاوز ذلك معايير التقييم.",

  // submit form — cost estimate
  costEstimating: "جارٍ تقدير التكلفة...",
  costEstimatePrefix: "تكلفة الـ API المقدَّرة: $",
  costUnavailable: "تقدير التكلفة غير متاح لهذا النموذج",

  // submit form — Turnstile failure block
  turnstileFailedLine1Prefix:
    "تعذّر إكمال فحص التحقق البشري. ثمة شيء ما يحجب أو يُبطئ ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — عادةً وضع خصوصية صارم في المتصفح (مثل منع التتبع في Safari أو وضع Firefox ETP الصارم)، أو حاجب محتوى/إعلانات (Brave Shields، أو uBlock Origin في بعض القوائم)، أو شبكة بطيئة أو مُرشَّحة.",
  turnstileFailedLine2Prefix: "جرِّب إعادة تحميل الصفحة أولًا. وإذا استمرت المشكلة، فاسمح لـ ",
  turnstileFailedLine2Mid: " من أجل ",
  turnstileFailedLine2Suffix:
    " (بتعطيل حواجب المحتوى أو تخفيف إعدادات الخصوصية)، أو استخدم متصفحًا مختلفًا. وعلى عنوان معاينة، قد يحتاج النشر أيضًا إلى إدراج اسم المضيف هذا في قائمة السماح الخاصة بأداة Cloudflare Turnstile.",
  turnstileFailedLine3Prefix: "أو شغّل coarse محليًا بمفتاح OpenRouter الخاص بك: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  // submit form — buttons + handoff picker
  submitButton: "راجِع ورقتي",
  submitButtonBusy: "جارٍ الإرسال...",
  submitOr: "أو",
  handoffButton: "راجِع باستخدام اشتراكي ▾",
  handoffButtonBusy: "جارٍ التحضير...",

  // submit form — handoff progress messages
  handoffUploading: "جارٍ رفع الورقة...",
  handoffPreparing: "جارٍ تحضير التسليم...",

  // submit form — explanatory paragraphs
  explainReviewLabel: "راجِع ورقتي:",
  explainReviewBody:
    " يتولّى OpenRouter كل شيء من البداية إلى النهاية. يُحذف الملف بعد المعالجة. يعمل مفتاح المراجعة لمدة 90 يومًا. وعادةً أقل من $2.",
  explainSubscriptionLabel: "راجِع باستخدام اشتراكي:",
  explainSubscriptionPart1:
    "نمنحك أمر صدفة (shell) يشغّل خط أنابيب coarse الكامل محليًا باستخدام ",
  explainSubscriptionYour: "اشتراكك في",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: "،",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: "، أو",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "لإجراء استدلال الـ LLM.",
  explainSubscriptionPdf:
    "تدفع نحو $0.10 فقط لخطوة Mistral OCR المحلية (بمفتاح OpenRouter الخاص بك)؛ أما الملفات غير الـ PDF (.tex, .md, .docx، …) فتتخطى الـ OCR ولا تحتاج إلى مفتاح OpenRouter.",
  explainSubscriptionNonPdf:
    "ملفك ليس PDF، لذا تُتخطى خطوة Mistral OCR بالكامل — ويغطي اشتراكك التشغيل بأكمله، دون حاجة إلى مفتاح OpenRouter.",
  explainSubscriptionPart3: "تظهر المراجعة على هذه الصفحة عند الانتهاء.",
  explainDisclaimer:
    "يعمل محليًا على جهازك باستخدام حسابك الخاص في Claude Code أو Codex أو Gemini CLI. لا يتلقّى coarse.ink بيانات تسجيل دخول مزوّدك ولا يخزّنها، وتسري شروط مزوّدك وحدود استخدامه وسياسات مؤسسته. وليس coarse.ink تابعًا لـ Anthropic أو OpenAI أو Google.",

  // submit form — handoff result card
  handoffReviewWithPrefix: "راجِع باستخدام ",
  handoffModelLabel: "النموذج",
  handoffEffortLabel: "الجهد",
  handoffPastePromptPrefix: "الصق هذا الموجِّه في طرفية ",
  handoffPastePromptSuffix: " الخاصة بك:",
  handoffRunHint:
    "سيحدّث الوكيل مهارة coarse-review، ويشغّل المراجعة الكاملة محليًا، مستغرقًا 10–25 دقيقة. وتبقى بيانات تسجيل دخول مزوّدك على جهازك.",
  handoffKeyNeededPrefix:
    "يجب أن يكون مفتاح OpenRouter على جهازك أولًا — صدّر ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: "، أو ضعه في ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " أو ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    ". لا نمرّره عبر المتصفح لأن عنوان التسليم ينتهي به المطاف في سجل محادثة وكيلك. وإذا كان مفقودًا، فسيطلبه الوكيل.",
  handoffKeyNotNeeded:
    "لا حاجة إلى مفتاح OpenRouter لهذه الورقة — فهي ليست PDF، لذا يعمل الاستخراج محليًا دون خطوة Mistral OCR.",
  handoffReviewUrlIntro: "عند انتهاء المراجعة، ستظهر على:",
  handoffInstallPrefix: "ألا تملك ",
  handoffInstallSuffix: " بعد؟ ",
  handoffInstallLink: "ثبّته →",

  // retrieve
  findReviewHeading: "ابحث عن مراجعة",
  findReviewPlaceholder: "الصق مفتاح المراجعة أو رابط المراجعة الكامل أو معرّف المراجعة القديم...",
  findReviewAriaLabel: "مفتاح المراجعة",
  findReviewButton: "بحث",

  // footer
  footerPrivacy: "الخصوصية",
  footerTerms: "الشروط",
  footerContact: "اتصل بنا",

  // status / errors (set in handlers)
  noticeKeyMigrated:
    "تم نقل مفتاح OpenRouter المحفوظ إلى تخزين خاص بهذه التبويبة فقط. وسيُمحى عند إغلاق هذه التبويبة.",
  errorLoginNoPersist:
    "تم تسجيل الدخول، لكن تعذّر الاحتفاظ بالمفتاح في هذه التبويبة. ستحتاج إلى لصقه مرة أخرى إذا أُعيد تحميل هذه الصفحة.",
  errorLoginFailed:
    "فشل تسجيل الدخول إلى OpenRouter. يُرجى المحاولة مرة أخرى أو لصق مفتاح يدويًا.",
  errorAuthFailed:
    "فشلت المصادقة. على عمليات نشر المعاينة، يعني ذلك عادةً أن بيانات Basic Auth المخزّنة مؤقتًا في المتصفح لم تُرسَل عند تقديم النموذج. أعد تحميل التبويبة (Cmd/Ctrl+Shift+R)، وسجّل الدخول مرة أخرى عند مطالبة كلمة المرور، ثم أعِد المحاولة.",
  errorServiceUnavailable: "الخدمة غير متاحة مؤقتًا — يُرجى المحاولة مرة أخرى بعد دقيقة.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "تعذّر تحميل أداة التحقق البشري لدينا — على الأرجح يحجب امتداد متصفح (Brave Shields، أو uBlock Origin، أو Firefox ETP الصارم) challenges.cloudflare.com. جرِّب تعطيله من أجل ",
  errorTurnstileBlockedSuffix: "، أو شغّل coarse محليًا: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "لا يزال انتظار تحميل التحقق البشري جاريًا — امهله لحظة وحاول مرة أخرى.",
  errorPrepareUpload: "فشل تحضير الرفع",
  errorUploadFailed: "فشل رفع الملف — يُرجى المحاولة مرة أخرى",
  errorSubmissionFailed: "فشل الإرسال",
  errorHandoffFailed: "فشل التسليم",
  launchCommandCopied: "تم نسخ الأمر إلى الحافظة. الصقه في طرفيتك.",
  launchOpeningCodex:
    "جارٍ فتح تطبيق سطح المكتب Codex — يُفترض أن يُملأ المحرِّر مسبقًا. اضغط على إرسال.",
  launchOpeningPrefix: "جارٍ فتح ",
  launchOpeningSuffix: " — الصق الموجِّه من حافظتك (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " لم يُفتح تطبيق سطح المكتب. إذا كنت تملك إصدار واجهة سطر الأوامر فقط، فالصق الأوامر أعلاه في طرفيتك بدلًا من ذلك.",
  errorLoginCouldNotStartPrefix: "تعذّر بدء تسجيل الدخول إلى OpenRouter: ",

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "لغة المراجعة",
  reviewLanguageAuto: "تلقائي — مطابقة لغة الورقة",
  reviewLanguageHelper:
    "تُعتمد افتراضيًا لغة الورقة نفسها؛ وتبقى الاقتباسات دائمًا بلغتها الأصلية.",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "النموذج",
  modelPickerUnavailableTitle: "غير متاح حاليًا",
  modelPickerSearchPlaceholder: "ابحث في النماذج...",
  modelPickerLoading: "جارٍ تحميل النماذج...",
  modelPickerNoResults: "لم يُعثر على أي نماذج.",
  modelPickerSearch: "ابحث في النماذج...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "متصل بـ OpenRouter",
  openRouterLogOut: "تسجيل الخروج",
  openRouterLogIn: "سجّل الدخول عبر OpenRouter →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "تتطلب هذه المراجعة رابط المراجعة الآمن الكامل أو مفتاح المراجعة.",
  statusLoadFailed: "فشل تحميل حالة المراجعة. يُرجى المحاولة مرة أخرى.",
  statusCancelledByUser: "أُلغيت المراجعة من قِبل المستخدم",
  statusLoading: "جارٍ التحميل",
  statusAccessTokenRequired: "رمز الوصول مطلوب.",
  statusNotFoundHeading: "لم يُعثر على المراجعة.",
  statusNotFoundBody: "تحقّق من مفتاح المراجعة وحاول مرة أخرى.",
  statusCancelConfirmHeading: "إلغاء المراجعة؟",
  statusCancelConfirmBody: "هل أنت متأكد؟ لن تتمكن من رؤية نتائجك.",
  statusCancelling: "جارٍ الإلغاء...",
  statusYesCancel: "نعم، ألغِ",
  statusGoBack: "العودة",
  statusLabelCancelled: "أُلغيت",
  statusLabelFailed: "فشلت",
  statusLabelReviewing: "قيد المراجعة",
  statusLabelQueued: "في قائمة الانتظار",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "جارٍ قراءة ورقتك.",
  statusQueuedHeading: "في قائمة الانتظار.",
  statusRunningBody: "جارٍ تشغيل خط أنابيب المراجعة (عادةً 30–60 دقيقة).",
  statusQueuedBody: "مراجعتك في قائمة الانتظار وستبدأ قريبًا.",
  statusEmailWhenDone: "سنرسل إليك بريدًا إلكترونيًا عند الانتهاء.",
  statusCancelledHeading: "أُلغيت المراجعة.",
  statusCancelledBody:
    "وُسمت المهمة المُدرَجة في قائمة الانتظار بأنها مُلغاة. وإذا كان العمل قد بدأ بالفعل، فقد يستغرق المُعالِج بعض الوقت ليتوقف.",
  statusFailedHeading: "فشلت.",
  statusUnexpectedError: "حدث خطأ غير متوقع.",
  statusResubmitPrefix: "يُرجى إعادة الإرسال، أو انشر مشكلتك على ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: ".",
  statusTryAgain: "حاول مرة أخرى →",
  statusKeyBoxSave: "مفتاح مراجعتك — احفظ هذا",
  statusKeyBoxLegacy: "رابط المراجعة القديم",
  statusCopied: "تم النسخ",
  statusCopyLink: "نسخ الرابط",
  statusRedirectNote: "ستُعاد توجيه هذه الصفحة تلقائيًا عندما تصبح مراجعتك جاهزة.",
  statusCancelReview: "إلغاء المراجعة",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "تتطلب هذه المراجعة رابط المراجعة الآمن الكامل أو مفتاح المراجعة.",
  reviewClientLoadFailed: "فشل تحميل المراجعة. يُرجى المحاولة مرة أخرى.",
  reviewClientLoading: "جارٍ التحميل",
  reviewClientNotFoundHeading: "لم يُعثر على المراجعة.",
  reviewClientNotFoundBody: "تحقّق من مفتاحك وحاول مرة أخرى.",
  reviewClientSubmitNewPaper: "أرسِل ورقة جديدة →",
  reviewClientAccessTokenRequired: "رمز الوصول مطلوب.",
  reviewClientBackHome: "العودة إلى الصفحة الرئيسية →",
  reviewClientReadingHeading: "جارٍ قراءة ورقتك.",
  reviewClientQueuedHeading: "في قائمة الانتظار.",
  reviewClientRunningBody: "عادةً 30–60 دقيقة. تُحدَّث هذه الصفحة تلقائيًا.",
  reviewClientQueuedBody: "تبدأ المعالجة قريبًا.",
  reviewClientFailedHeading: "فشلت المراجعة.",
  reviewClientUnexpectedError: "حدث خطأ غير متوقع.",
  reviewClientTryAgain: "حاول مرة أخرى →",
  reviewClientCancelledHeading: "أُلغيت المراجعة.",
  reviewClientCancelledBody: "أُلغيت هذه المراجعة قبل اكتمالها.",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "عرض أقل",
  reviewShowMore: "عرض المزيد",
  reviewShowInPaper: "عرض في الورقة",
  reviewMarkActive: "تعيين كنشط",
  reviewMarkDone: "تعيين كمنجز",
  reviewDismiss: "تجاهل",
  reviewDiscuss: "ناقش",
  reviewDiscussTitle: "ناقش هذا التعليق مع نموذج ذكاء اصطناعي",
  reviewShowDetails: "عرض التفاصيل",
  reviewStatusDone: "منجز",
  reviewStatusDismissed: "مُتجاهَل",
  reviewHide: "إخفاء",
  reviewFilterAll: "الكل",
  reviewFilterActive: "نشط",
  reviewFilterDone: "منجز",
  reviewFilterDismissed: "مُتجاهَل",
  reviewSidebarOverallFeedback: "الملاحظات العامة",
  reviewSidebarCommentsPrefix: "التعليقات (",
  reviewSidebarCommentsRemainingSuffix: " متبقٍ)",
  reviewRemainingSuffix: " متبقٍ",
  reviewDownload: "تنزيل",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "طباعة / PDF",
  reviewHidePaper: "إخفاء الورقة",
  reviewShowPaper: "عرض الورقة",
  reviewCopied: "تم النسخ",
  reviewShare: "مشاركة",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "اسحب لتغيير حجم لوحة الورقة",
  reviewResizeTitle: "اسحب لتغيير الحجم",
  reviewOfPrefix: "مراجعة ",
  reviewMetaModel: "النموذج",
  reviewMetaDate: "التاريخ",
  reviewMetaDomain: "المجال",
  reviewMetaTime: "الوقت",
  reviewMetaCost: "التكلفة",
  reviewMetaReviewLanguage: "لغة المراجعة",
  reviewMetaAutoDetectedSuffix: " · مكتشَفة تلقائيًا",
  reviewOverallFeedbackHeading: "الملاحظات العامة",
  reviewDetailedCommentsPrefix: "التعليقات المفصّلة (",
  reviewDetailedCommentsSuffix: ")",
  reviewGeneratedByPrefix: "أُنشئت بواسطة ",
  reviewGeneratedBySuffix: ". بالطبع.",
  reviewShareThisReview: "شارك هذه المراجعة",
  reviewDeleteReview: "حذف المراجعة",
  reviewDeleteConfirmHeading: "حذف المراجعة؟",
  reviewDeleteConfirmBody: "هل أنت متأكد؟ لن تتمكن من رؤية نتائجك.",
  reviewDeleting: "جارٍ الحذف...",
  reviewYesDelete: "نعم، احذف",
  reviewGoBack: "العودة",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "هل هذا النقد صحيح فعلًا؟",
  chatExamplePrompt2: "كيف ينبغي أن أنقّح الورقة لمعالجته؟",
  chatExamplePrompt3: "أين ينطبق هذا في الورقة؟",
  chatNoResponse: "لا توجد استجابة من النموذج. حاول مرة أخرى أو بدّل النماذج.",
  chatSessionExpired: "انتهت صلاحية جلسة OpenRouter الخاصة بك. سجّل الدخول مرة أخرى للمتابعة.",
  chatSomethingWrong: "حدث خطأ ما.",
  chatDiscussKicker: "ناقش · ",
  chatKickerComment: "التعليق رقم ",
  chatKickerOverallFeedback: "الملاحظات العامة",
  chatDiscussAriaPrefix: "ناقش: ",
  chatCloseAriaLabel: "إغلاق المحادثة",
  chatDisconnectKeyTitle:
    "افصل مفتاح OpenRouter الخاص بك (لا يُخزَّن بعد إغلاق هذه التبويبة)",
  chatDisconnectKey: "فصل المفتاح",
  chatInputPlaceholder: "اسأل عن هذا التعليق…",
  chatMessageAriaLabel: "رسالة",
  chatStop: "إيقاف",
  chatSend: "إرسال",
  chatModelDisclosurePrefix: "النموذج: ",
  chatKeyGateIntro:
    "اتصل بـ OpenRouter للمحادثة حول هذا التعليق. يُرسَل مفتاحك مباشرةً إلى OpenRouter — لا إلى خوادمنا أبدًا — ويُمحى عند إغلاق هذه التبويبة.",
  chatKeyGateOrPaste: "— أو الصق مفتاحًا —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "مفتاح OpenRouter API",
  chatKeyGateUseKey: "استخدم المفتاح",
  chatKeyGateHelper:
    "تبقى مفاتيح OAuth في هذه التبويبة فقط وتُمحى عند إغلاقها. ولا تُحفظ أبدًا على خوادمنا.",
  chatEmptyHintPrefix: "اسأل أي شيء عن هذا التعليق. ترسل كل رسالة ",
  chatEmptyHintFullPaper: "الورقة الكاملة",
  chatEmptyHintQuotedPassage: "المقطع المقتبس والملاحظات",
  chatEmptyHintSuffix: " بوصفها سياقًا، وتعمل على رصيد OpenRouter الخاص بك.",
  chatEmptyHintNoPaper:
    "نص الورقة الكامل غير مخزَّن لهذه المراجعة، لذا تعتمد الإجابات على المقطع المقتبس والملاحظات فقط.",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "فُتح ",
  handoffMenuOpenedPromptMid: " مع تعبئة الموجِّه مسبقًا — أرفِق coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md، ثم أرسِل. (نُسخ الموجِّه أيضًا، تحسّبًا فقط.)",
  handoffMenuOpenedPlainMid: " — أرفِق coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md والصق الموجِّه المنسوخ.",
  handoffMenuButtonTitle:
    "أرسِل الورقة + المراجعة إلى محادثة الذكاء الاصطناعي الخاصة بك (Claude، ChatGPT، Gemini، Grok، DeepSeek)",
  handoffMenuButton: "ناقش مع ذكائك الاصطناعي",
  handoffMenuDownloadsIntro: "يُنزّل الورقة + المراجعة، ثم يفتح:",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "الورقة",
  paperPanelDownload: "تنزيل",
  paperPanelDownloadAriaLabel: "تنزيل ملف Markdown الخاص بالورقة",
  paperPanelCloseAriaLabel: "إغلاق لوحة الورقة",
};
