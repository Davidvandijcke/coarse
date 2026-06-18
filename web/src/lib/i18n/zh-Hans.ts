// Simplified Chinese (zh-Hans) site-UI catalog. Mirrors the keys of ./en.ts
// exactly; only the values are translated. Brand/technical tokens (coarse,
// OpenRouter, Claude Code, Codex, Gemini CLI, commands, URLs, model IDs) and
// glyphs are kept verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix
// fragments are significant and match en.ts (they concatenate with English
// brand tokens and runtime values).

import type { Messages } from "@/lib/i18n";

export const zhHans: Messages = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "网站语言",

  // copy-to-clipboard code block
  codeBlockCopied: "已复制 ✓",
  codeBlockCopy: "复制",

  // header
  headerTagline: "同行评审是一种公共产品。",
  navSetup: "设置",
  navSideBySide: "并排对比",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "投稿已暂时暂停。",
  bannerBusyPrefix: "系统繁忙（",
  bannerBusySuffix: " 个名额正在使用中）。你的评审可能会进入队列。",
  bannerFasterPrefix: "想要更快的结果，请试试 CLI：",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "嘿 ",
  heroGreetingSuffix: " 能帮我评审这篇论文吗？",
  heroHeading: "‘coarse!",
  heroLede:
    "AI 智能体评审你的论文并撰写审稿报告。你直接支付 API 费用。无需账户。",
  heroManifesto:
    "学术同行评审依靠无偿的学术劳动运转。有些人却决定借此牟利。我们对此并不认同。",

  // hero — score preview
  scoreVsOthers: "对比其他 AI 评审工具",
  statCostNum: "< $2*",
  statCostLabel: "每次评审",
  statCostFootnote: "*通常如此 :)",
  statCommentsNum: "20+",
  statCommentsLabel: "条详细评论",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "开源",

  // hero — competitive comparison
  comparePrefix: "盲测对比",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "在覆盖度、针对性和深度上得分更高——而成本只是其中的一小部分。",
  compareLink: "查看并排对比 →",

  // submit form — section heading + paper field
  formSubmitHeading: "提交论文",
  fieldPaper: "论文",
  dropzoneAriaLabel: "上传你的论文——拖入文件或点击浏览",
  dropzoneInputAriaLabel: "选择要上传的文件",
  dropzoneReplaceSuffix: " MB——点击或拖入以替换",
  dropzonePromptPrefix: "将文件拖到这里，或者 ",
  dropzoneBrowse: "浏览",
  dropzoneMaxSize: "最大 50 MB",

  // submit form — email field
  fieldEmail: "电子邮箱 ",
  fieldEmailQualifier: "（仅用于网页评审）",
  emailPlaceholderUnavailable: "— 不可用 —",
  emailPlaceholder: "you@university.edu",
  emailAriaLabel: "电子邮箱地址",
  emailHelperDisabled:
    "邮件投递暂时中断。提交时请保存好你的评审密钥，大约一小时后再回来查看。",
  emailHelperPrefix:
    "完成后我们会通过邮件通知你。如果没有收到，请检查你的垃圾邮件文件夹。",

  // submit form — OpenRouter key field
  fieldKey: "OpenRouter 密钥",
  fieldKeyGetOne: "获取密钥 →",
  keyOrPaste: "— 或粘贴密钥 —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter API 密钥",
  keyHelper:
    "OAuth 密钥仅保留在此标签页中，关闭后即清除。绝不会保存在我们的服务器上。",

  // submit form — author notes
  fieldNotes: "给评审者的备注",
  fieldNotesOptional: "（可选）",
  notesPlaceholder:
    "例如：请重点关注 §3 中的识别策略——数据部分目前仍是占位内容。",
  notesAriaLabel: "用于引导评审者的可选备注",
  notesHelper: "引导评审者的关注重点。不会覆盖评审标准。",

  // submit form — cost estimate
  costEstimating: "正在估算费用...",
  costEstimatePrefix: "预计 API 费用：$",
  costUnavailable: "无法估算该模型的费用",

  // submit form — Turnstile failure block
  turnstileFailedLine1Prefix:
    "我们的人机验证无法完成。有什么东西正在阻止或拖慢 ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " ——通常是浏览器的严格隐私模式（例如 Safari 的跟踪保护或 Firefox ETP 严格模式）、内容/广告拦截器（Brave Shields、某些过滤列表中的 uBlock Origin），或者是缓慢或经过过滤的网络。",
  turnstileFailedLine2Prefix: "请先尝试重新加载页面。如果问题仍然存在，请允许 ",
  turnstileFailedLine2Mid: " 访问 ",
  turnstileFailedLine2Suffix:
    " （关闭内容拦截器或放宽隐私设置），或者换用其他浏览器。在预览 URL 上，部署可能还需要将该主机名加入 Cloudflare Turnstile 小组件的允许列表。",
  turnstileFailedLine3Prefix: "或者用你自己的 OpenRouter 密钥在本地运行 coarse： ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: "。",

  // submit form — buttons + handoff picker
  submitButton: "评审我的论文",
  submitButtonBusy: "正在提交...",
  submitOr: "或",
  handoffButton: "用我的订阅来评审 ▾",
  handoffButtonBusy: "正在准备...",

  // submit form — handoff progress messages
  handoffUploading: "正在上传论文...",
  handoffPreparing: "正在准备交接...",

  // submit form — explanatory paragraphs
  explainReviewLabel: "评审我的论文：",
  explainReviewBody:
    " OpenRouter 全程处理一切。文件在处理后即被删除。评审密钥有效期为 90 天。通常不到 $2。",
  explainSubscriptionLabel: "用我的订阅来评审：",
  explainSubscriptionPart1:
    "我们会给你一条 shell 命令，让它使用 ",
  explainSubscriptionYour: "你自己的",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: "、",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: "，或",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "订阅进行 LLM 推理，在本地运行完整的 coarse 流水线。",
  explainSubscriptionPdf:
    "你只需为本地的 Mistral OCR 步骤支付约 ~$0.10（使用你自己的 OpenRouter 密钥）；非 PDF 上传（.tex, .md, .docx, …）会跳过 OCR，无需 OpenRouter 密钥。",
  explainSubscriptionNonPdf:
    "你的文件不是 PDF，因此会完全跳过 Mistral OCR 步骤——整个运行都由你的订阅承担，无需 OpenRouter 密钥。",
  explainSubscriptionPart3: "完成后评审会显示在本页面上。",
  explainDisclaimer:
    "在你本地的机器上，使用你自己的 Claude Code、Codex 或 Gemini CLI 账户运行。coarse.ink 不会接收或存储你的提供商登录信息，并且你的提供商的条款、使用限额和组织政策均适用。coarse.ink 与 Anthropic、OpenAI 或 Google 无任何关联。",

  // submit form — handoff result card
  handoffReviewWithPrefix: "用 ",
  handoffModelLabel: "模型",
  handoffEffortLabel: "强度",
  handoffPastePromptPrefix: "将这段提示词粘贴到你的 ",
  handoffPastePromptSuffix: " 终端中：",
  handoffRunHint:
    "智能体会刷新 coarse-review 技能，在本地运行完整评审，耗时 10–25 分钟。你的提供商登录信息会保留在你的机器上。",
  handoffKeyNeededPrefix:
    "你的 OpenRouter 密钥需要先放到你的机器上——请导出 ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: "，或将其放入 ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " 或 ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    "。我们不会通过浏览器传递它，因为交接 URL 最终会出现在你智能体的聊天记录中。如果缺失，智能体会主动询问。",
  handoffKeyNotNeeded:
    "这篇论文不需要 OpenRouter 密钥——它不是 PDF，因此提取会在本地运行，无需 Mistral OCR 步骤。",
  handoffReviewUrlIntro: "评审完成后，将显示在：",
  handoffInstallPrefix: "还没有 ",
  handoffInstallSuffix: " 吗？ ",
  handoffInstallLink: "安装它 →",

  // retrieve
  findReviewHeading: "查找评审",
  findReviewPlaceholder: "粘贴你的评审密钥、完整评审链接或旧版评审 ID...",
  findReviewAriaLabel: "评审密钥",
  findReviewButton: "查找",

  // footer
  footerPrivacy: "隐私",
  footerTerms: "条款",
  footerContact: "联系",

  // status / errors (set in handlers)
  noticeKeyMigrated:
    "已将你保存的 OpenRouter 密钥移入仅限本标签页的存储。关闭此标签页时它将被清除。",
  errorLoginNoPersist:
    "已登录，但无法在本标签页中保留密钥。如果此页面重新加载，你需要再次粘贴它。",
  errorLoginFailed:
    "OpenRouter 登录失败。请重试，或手动粘贴密钥。",
  errorAuthFailed:
    "身份验证失败。在预览部署上，这通常意味着浏览器缓存的 Basic Auth 凭据在提交表单时没有被发送。请刷新标签页（Cmd/Ctrl+Shift+R），在密码提示处重新登录，然后重试。",
  errorServiceUnavailable: "服务暂时不可用——请一分钟后重试。",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "我们的人机验证小组件无法加载——很可能是浏览器扩展（Brave Shields、uBlock Origin、Firefox ETP 严格模式）拦截了 challenges.cloudflare.com。请尝试为以下对象将其停用： ",
  errorTurnstileBlockedSuffix: "，或在本地运行 coarse：uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "仍在等待人机验证加载——请稍等片刻再重试。",
  errorPrepareUpload: "准备上传失败",
  errorUploadFailed: "文件上传失败——请重试",
  errorSubmissionFailed: "提交失败",
  errorHandoffFailed: "交接失败",
  launchCommandCopied: "命令已复制到剪贴板。请将其粘贴到你的终端中。",
  launchOpeningCodex:
    "正在打开 Codex 桌面应用——编辑框应已预先填好。点击发送即可。",
  launchOpeningPrefix: "正在打开 ",
  launchOpeningSuffix: " ——请从剪贴板粘贴提示词（⌘V / Ctrl+V）。",
  launchDidntOpenSuffix:
    " 桌面应用未能打开。如果你只安装了 CLI 版本，请改为将上面的命令粘贴到你的终端中。",
  errorLoginCouldNotStartPrefix: "OpenRouter 登录无法启动： ",

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "评审语言",
  reviewLanguageAuto: "自动——匹配论文的语言",
  reviewLanguageHelper:
    "默认使用论文本身的语言；引文始终保留原文。",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "模型",
  modelPickerUnavailableTitle: "当前不可用",
  modelPickerSearchPlaceholder: "搜索模型...",
  modelPickerLoading: "正在加载模型...",
  modelPickerNoResults: "未找到模型。",
  modelPickerSearch: "搜索模型...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "已连接到 OpenRouter",
  openRouterLogOut: "退出登录",
  openRouterLogIn: "使用 OpenRouter 登录 →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "查看此评审需要完整的安全评审链接或评审密钥。",
  statusLoadFailed: "加载评审状态失败。请重试。",
  statusCancelledByUser: "评审已被用户取消",
  statusLoading: "正在加载",
  statusAccessTokenRequired: "需要访问令牌。",
  statusNotFoundHeading: "未找到评审。",
  statusNotFoundBody: "请检查评审密钥后重试。",
  statusCancelConfirmHeading: "取消评审？",
  statusCancelConfirmBody: "确定吗？你将无法查看你的结果。",
  statusCancelling: "正在取消...",
  statusYesCancel: "是，取消",
  statusGoBack: "返回",
  statusLabelCancelled: "已取消",
  statusLabelFailed: "失败",
  statusLabelReviewing: "评审中",
  statusLabelQueued: "排队中",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "正在阅读你的论文。",
  statusQueuedHeading: "已排队。",
  statusRunningBody: "正在运行评审流水线（通常需要 30–60 分钟）。",
  statusQueuedBody: "你的评审已排队，即将开始。",
  statusEmailWhenDone: "完成后我们会通过邮件通知你。",
  statusCancelledHeading: "评审已取消。",
  statusCancelledBody:
    "排队中的任务已被标记为取消。如果工作已经开始，工作进程可能需要一点时间才能停下来。",
  statusFailedHeading: "失败。",
  statusUnexpectedError: "发生了意外错误。",
  statusResubmitPrefix: "请尝试重新提交，或在 ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: " 上反馈你的问题。",
  statusTryAgain: "重试 →",
  statusKeyBoxSave: "你的评审密钥——请保存好",
  statusKeyBoxLegacy: "旧版评审链接",
  statusCopied: "已复制",
  statusCopyLink: "复制链接",
  statusRedirectNote: "评审准备就绪后，本页面将自动跳转。",
  statusCancelReview: "取消评审",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "查看此评审需要完整的安全评审链接或评审密钥。",
  reviewClientLoadFailed: "加载评审失败。请重试。",
  reviewClientLoading: "正在加载",
  reviewClientNotFoundHeading: "未找到评审。",
  reviewClientNotFoundBody: "请检查你的密钥后重试。",
  reviewClientSubmitNewPaper: "提交新论文 →",
  reviewClientAccessTokenRequired: "需要访问令牌。",
  reviewClientBackHome: "返回首页 →",
  reviewClientReadingHeading: "正在阅读你的论文。",
  reviewClientQueuedHeading: "已排队。",
  reviewClientRunningBody: "通常需要 30–60 分钟。本页面会自动更新。",
  reviewClientQueuedBody: "处理即将开始。",
  reviewClientFailedHeading: "评审失败。",
  reviewClientUnexpectedError: "发生了意外错误。",
  reviewClientTryAgain: "重试 →",
  reviewClientCancelledHeading: "评审已取消。",
  reviewClientCancelledBody: "此评审在完成前已被取消。",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "收起",
  reviewShowMore: "展开",
  reviewShowInPaper: "在论文中显示",
  reviewMarkActive: "标记为活跃",
  reviewMarkDone: "标记为完成",
  reviewDismiss: "忽略",
  reviewDiscuss: "讨论",
  reviewDiscussTitle: "与 AI 模型讨论此评论",
  reviewShowDetails: "显示详情",
  reviewStatusDone: "已完成",
  reviewStatusDismissed: "已忽略",
  reviewHide: "隐藏",
  reviewFilterAll: "全部",
  reviewFilterActive: "活跃",
  reviewFilterDone: "已完成",
  reviewFilterDismissed: "已忽略",
  reviewSidebarOverallFeedback: "总体反馈",
  reviewSidebarCommentsPrefix: "评论（",
  reviewSidebarCommentsRemainingSuffix: " 条待处理）",
  reviewRemainingSuffix: " 条待处理",
  reviewDownload: "下载",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "打印 / PDF",
  reviewHidePaper: "隐藏论文",
  reviewShowPaper: "显示论文",
  reviewCopied: "已复制",
  reviewShare: "分享",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "拖动以调整论文面板大小",
  reviewResizeTitle: "拖动以调整大小",
  reviewOfPrefix: "评审： ",
  reviewMetaModel: "模型",
  reviewMetaDate: "日期",
  reviewMetaDomain: "领域",
  reviewMetaTime: "耗时",
  reviewMetaCost: "费用",
  reviewMetaReviewLanguage: "评审语言",
  reviewMetaAutoDetectedSuffix: " · 自动检测",
  reviewOverallFeedbackHeading: "总体反馈",
  reviewDetailedCommentsPrefix: "详细评论（",
  reviewDetailedCommentsSuffix: "）",
  reviewGeneratedByPrefix: "由 ",
  reviewGeneratedBySuffix: " 生成。当然了。",
  reviewShareThisReview: "分享此评审",
  reviewDeleteReview: "删除评审",
  reviewDeleteConfirmHeading: "删除评审？",
  reviewDeleteConfirmBody: "确定吗？你将无法查看你的结果。",
  reviewDeleting: "正在删除...",
  reviewYesDelete: "是，删除",
  reviewGoBack: "返回",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "这条批评意见真的成立吗？",
  chatExamplePrompt2: "我该如何修改才能解决它？",
  chatExamplePrompt3: "论文中的哪一处适用于此？",
  chatNoResponse: "模型没有响应。请重试或切换模型。",
  chatSessionExpired: "你的 OpenRouter 会话已过期。请重新登录以继续。",
  chatSomethingWrong: "出了点问题。",
  chatDiscussKicker: "讨论 · ",
  chatKickerComment: "评论 #",
  chatKickerOverallFeedback: "总体反馈",
  chatDiscussAriaPrefix: "讨论： ",
  chatCloseAriaLabel: "关闭聊天",
  chatDisconnectKeyTitle:
    "断开你的 OpenRouter 密钥（它不会保存到本标签页之外）",
  chatDisconnectKey: "断开密钥",
  chatInputPlaceholder: "询问关于这条评论的问题…",
  chatMessageAriaLabel: "消息",
  chatStop: "停止",
  chatSend: "发送",
  chatModelDisclosurePrefix: "模型： ",
  chatKeyGateIntro:
    "连接 OpenRouter 即可讨论这条评论。你的密钥会直接发送给 OpenRouter——绝不会发送到我们的服务器——并在你关闭此标签页时清除。",
  chatKeyGateOrPaste: "— 或粘贴密钥 —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "OpenRouter API 密钥",
  chatKeyGateUseKey: "使用密钥",
  chatKeyGateHelper:
    "OAuth 密钥仅保留在此标签页中，关闭后即清除。绝不会保存在我们的服务器上。",
  chatEmptyHintPrefix: "可以就这条评论提出任何问题。每条消息都会将 ",
  chatEmptyHintFullPaper: "整篇论文",
  chatEmptyHintQuotedPassage: "引用的段落和反馈",
  chatEmptyHintSuffix: " 作为上下文发送，并消耗你的 OpenRouter 额度运行。",
  chatEmptyHintNoPaper:
    "本评审未存储论文全文，因此回答仅依据引用的段落和反馈。",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "已打开 ",
  handoffMenuOpenedPromptMid: "，提示词已预先填好——请附上 coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md，然后发送。（提示词也已复制，以防万一。）",
  handoffMenuOpenedPlainMid: " ——请附上 coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md，并粘贴已复制的提示词。",
  handoffMenuButtonTitle:
    "将论文 + 评审发送到你自己的 AI 聊天（Claude、ChatGPT、Gemini、Grok、DeepSeek）",
  handoffMenuButton: "与你的 AI 讨论",
  handoffMenuDownloadsIntro: "下载论文 + 评审，然后打开：",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "论文",
  paperPanelDownload: "下载",
  paperPanelDownloadAriaLabel: "下载论文 markdown",
  paperPanelCloseAriaLabel: "关闭论文面板",

  // setup page (setup/page.tsx)
  // setup page — tab switcher
  setupTablistAriaLabel: "设置方式",
  setupTabOpenRouter: "OpenRouter 密钥",
  setupTabSubscription: "使用我的订阅",
  // setup page — OpenRouter tab intro
  setupOrHeading: "获取你的 OpenRouter 密钥",
  setupOrIntro:
    "大约需要 2 分钟。你需要一张信用卡来充值约 $1 的额度以便开始——你将在第 2 步中充值到 $20。",
  setupOrFasterLabel: "更快的方式：",
  setupOrFasterMid1: " 在主表单上你可以点击 ",
  setupOrFasterLogIn: "“使用 OpenRouter 登录”",
  setupOrFasterSuffix:
    " 来授权 coarse 并跳过手动创建密钥。你仍然需要一个有额度的 OpenRouter 账户（下面的第 1 步和第 2 步），并且我们仍然建议设置单个密钥的消费限额（第 4 步）。",
  // setup page — OpenRouter step 1
  setupOrStep1Title: "创建账户",
  setupOrStep1BodyPrefix: "前往 ",
  setupOrStep1BodySuffix: " 并点击“Get API Key”，或使用 Google / GitHub 注册。",
  setupOrStep1Annotation: "主页",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "面向 LLM 的统一 API——一把密钥，多种模型。",
  // setup page — OpenRouter step 2
  setupOrStep2Title: "充值额度",
  setupOrStep2BodyPrefix: "导航到 ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    "。至少充值 $20。便宜的开源模型每次评审约 $0.25；像 Claude Opus 或 GPT-5 这样的 SOTA 模型在长论文上可能花费 $5–$10。提交前显示的费用估算只是一个大致范围，不是上限。请预留余量，否则评审可能会中途耗尽密钥而失败。未使用的额度不会过期。",
  setupOrStep2Annotation: "额度页面",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "金额",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "Balance: $0.00",
  // setup page — OpenRouter step 3
  setupOrStep3Title: "创建 API 密钥",
  setupOrStep3BodyPrefix: "前往 ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: "，点击“Create Key”，并将其命名为 ",
  setupOrStep3BodySuffix: "。",
  setupOrStep3Provisioning:
    "请确保它是常规 API 密钥——而不是集成部分的预配/管理密钥。预配密钥可以创建和列出其他密钥，但无法运行推理，如果你粘贴了这种密钥，coarse 会报错“User not found”。",
  setupOrStep3CopyWarning: "立即复制密钥——你不会再看到它了。",
  setupOrStep3Annotation: "密钥页面",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "密钥名称",
  setupOrStep3MockYourKey: "你的密钥",
  // setup page — OpenRouter step 4
  setupOrStep4Title: "为密钥设置消费限额",
  setupOrStep4BodyPrefix: "在 ",
  setupOrStep4BodyLink: "Keys 页面",
  setupOrStep4BodyMid1: " 上，点击你新密钥旁边的 ",
  setupOrStep4BodyMid2: " 菜单，选择“Edit”，并将额度限额设置为 ",
  setupOrStep4BodyAtLeast: "至少 $20",
  setupOrStep4BodySuffix:
    "。一旦达到限额，密钥就会停止工作，因此不可能产生意外费用。但如果设置得太紧，单次昂贵的评审就可能在运行中途耗尽它。",
  setupOrStep4Annotation: "密钥菜单",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "此密钥的额度限额",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "为什么这很重要：",
  setupOrStep4WhyMid1: " coarse 是开源的——你可以 ",
  setupOrStep4WhyLink: "阅读每一行代码",
  setupOrStep4WhySuffix:
    "。你的密钥会直接发送给 OpenRouter 以运行评审，然后即被丢弃——它绝不会被存储。但你不必信任我们：单个密钥的限额保证了即使在最坏的情况下，它的花费也绝不会超过你所允许的额度。",
  setupOrStep4CostLabel: "关于费用估算的说明：",
  setupOrStep4CostBody:
    " 提交前显示的估算是一个带有约 15% 缓冲的启发式数值，不是硬性上限。在长论文上使用 SOTA 模型时，一旦证明验证和批评重写启动，实际费用可能高达估算的约 2 倍。如果单个密钥的上限正好卡在估算值上，一次棘手的评审就可能把它耗尽并在运行中途失败。请始终预留余量。",
  // setup page — OpenRouter step 5
  setupOrStep5Title: "粘贴到 coarse 中",
  setupOrStep5Body: "回到这里，将你的密钥粘贴到表单中，然后上传你的 PDF。",
  setupOrStep5Annotation: "coarse 表单",
  setupOrStep5MockEmail: "电子邮箱",
  setupOrStep5MockKey: "OpenRouter 密钥",
  setupOrStep5MockButton: "评审我的论文",
  // setup page — shared footer CTA
  setupReadyCta: "准备好了吗？评审你的论文 →",
  // setup page — subscription tab intro
  setupSubHeading: "使用你的编码智能体订阅",
  setupSubIntro1:
    "适用于已经在为 Claude Code、Codex 或 Gemini CLI 付费的用户。评审在你的订阅上运行并在那里计费。你只需为 OCR 环节向 OpenRouter 支付约 ~$0.15。",
  setupSubIntro2:
    "在你本地的机器上，使用你自己的 Claude Code、Codex 或 Gemini CLI 账户运行。coarse.ink 不会接收或存储你的提供商登录信息。你的提供商的条款和使用限额仍然适用。coarse.ink 与 Anthropic、OpenAI 或 Google 无任何关联。",
  // setup page — subscription step 1
  setupSubStep1Title: "安装编码智能体",
  setupSubStep1Body:
    "选择你为之付费的那一个。如果你没有付费，Gemini CLI 有免费层级。请从供应商自己的页面安装——他们的文档保持最新。",
  setupSubStep1ClaudePrice: "Anthropic Pro 或 Max",
  setupSubStep1CodexPrice: "ChatGPT Plus、Pro 或 Business",
  setupSubStep1GeminiPrice: "免费层级足以应对大多数论文",
  setupSubStep1InstallLabel: "安装说明 ↗",
  setupSubStep1Verify:
    "运行测试命令以验证安装 + 登录。如果它打印出响应，你就准备好了。",
  setupSubStep1CardLogin: "登录： ",
  setupSubStep1CardTest: "测试： ",
  // setup page — subscription step 2
  setupSubStep2Title: "在你的机器上放一把 OpenRouter 密钥（仅限 PDF）",
  setupSubStep2BodyPrefix:
    "此步骤仅适用于 PDF 论文——非 PDF 来源（.tex, .md, .docx, …）会在本地提取而无需 OCR，因此它们在任何地方都不需要 OpenRouter 密钥，你可以直接跳到第 3 步。对于 PDF，coarse 的 OCR 步骤仍需要 OpenRouter（每篇论文约 $0.10）。请按照 ",
  setupSubStep2BodyTab: "OpenRouter 密钥",
  setupSubStep2BodySuffix:
    " 标签页来创建账户、充值 $1 额度，并设置 $2 的单个密钥限额。这里不需要 OpenRouter-only 路径中的 $20 缓冲，因为评审本身是在你的编码智能体订阅上运行的。",
  setupSubStep2KeyPrefix: "然后把密钥放到你自己的机器上：运行 ",
  setupSubStep2KeyMid1: "，将其放入 ",
  setupSubStep2KeyMid2: "，或将其保存到 ",
  setupSubStep2KeySuffix:
    "。你的 CLI 在运行提取时会在本地读取它；coarse.ink 绝不会看到它。",
  // setup page — subscription step 3
  setupSubStep3Title: "上传你的论文并选择一个 CLI",
  setupSubStep3BodyPrefix: "在 ",
  setupSubStep3BodyLink: "主页面",
  setupSubStep3BodyMid: " 上，将你的论文（PDF、.tex、.md、.docx、…）拖到表单上，然后点击 ",
  setupSubStep3BodyButton: "用我的订阅来评审 ▾",
  setupSubStep3BodySuffix:
    " 下拉菜单并选择你的 CLI。coarse 会上传文件、铸造一个交接令牌，并显示你将在下一步粘贴的提示词。你不需要在这里的表单上粘贴你的 OpenRouter 密钥；CLI 会从你的机器上读取它（第 2 步）。",
  // setup page — subscription step 4
  setupSubStep4Title: "将提示词粘贴到你的 CLI 中",
  setupSubStep4BodyPrefix: "coarse 会给你一条自然语言提示词。从面板中复制它，将其粘贴到你的 ",
  setupSubStep4BodyMid1: "、",
  setupSubStep4BodyMid2: " 或 ",
  setupSubStep4BodyMid3: " 会话中，然后点击发送。智能体会刷新其技能包，在自己的子进程调用上运行完整的 coarse 流水线，并在完成后打印出一个 ",
  setupSubStep4BodySuffix:
    " URL。耗时 10–25 分钟。点击该 URL 即可在 coarse.ink 上打开完成的评审。",
  setupSubStep4TimeoutLabel: "如果你是粘贴到编码智能体中",
  setupSubStep4TimeoutSuffix:
    "（而非普通终端），请在发送提示词之前将其 bash 工具超时调高到至少 45 分钟。智能体的默认超时可能低至 2 分钟，远低于 10–25 分钟的评审运行时间。",
  // setup page — subscription step 5 (troubleshooting)
  setupSubStep5Title: "如果出了问题",
  setupSubTrouble1Symptom: "“Try opening Claude Code / Codex”按钮没有任何反应。",
  setupSubTrouble1Fix:
    "该按钮仅在你安装了桌面应用时才有效。如果只安装了 CLI，浏览器无法为你启动终端。请从面板中复制提示词并手动将其粘贴到你的 CLI 中。",
  setupSubTrouble2Symptom: "智能体运行中出现“No such command ‘install-skills’”。",
  setupSubTrouble2FixPrefix: "可以放心忽略。技能包仍会直接通过 ",
  setupSubTrouble2FixSuffix: " 加载；智能体会继续进行到评审步骤。",
  setupSubTrouble3Symptom: "评审之后我的 Anthropic / OpenAI / Google 账单上涨了。",
  setupSubTrouble3FixPrefix: "请检查你的 shell 环境中是否有 ",
  setupSubTrouble3FixMid1: "、",
  setupSubTrouble3FixMid2: " 或 ",
  setupSubTrouble3FixSuffix:
    "。如果设置了，宿主 CLI 会向 API 账户计费，而不是你的订阅。v1.3.0+ 会自动剥离这些变量，但旧版本不会。",
  setupSubTrouble4Symptom: "评论比平时少（约 10 条而不是 15–25 条）。",
  setupSubTrouble4FixPrefix: "某个章节触发了 30 分钟超时并被丢弃。在默认强度下很少见，使用 ",
  setupSubTrouble4FixSuffix:
    " 处理长论文时更常见。请重新运行；如果发生两次，就把强度降低一档。",

  // compare page (ComparePage.tsx)
  comparePanelErrorBody: "无法渲染这一个。请尝试其他模型或对比。",
  comparePaperCorticalCircuits: "皮层环路",
  comparePaperCosetCodes: "陪集码",
  comparePaperPopulationGenetics: "群体遗传学",
  comparePaperTargetingInterventions: "精准干预",
  compareScoresShow: "显示",
  compareScoresHide: "隐藏",
  compareScoresToggleSuffix: " 各篇论文的全部得分 ",
  compareScoresColPaper: "论文",
  compareScoresColReference: "参考",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "由 Gemini 3.1 Pro 通过 PDF 多模态输入评估。5.0/5 = 与参考质量相当。5.5+/5 = 超过参考质量。",
  compareJudgeShow: "显示",
  compareJudgeHide: "隐藏",
  compareJudgeToggleSuffix: " 发送给 Gemini 3.1 Pro 的评判提示词 ",
  compareJudgeExplain:
    "为减轻已知的 LLM-as-judge 偏差，评判器在每次评估中以两篇评审的呈现顺序互换的方式运行两次，并对两种顺序下的得分取平均。这可以抵消位置偏差，即评判者系统性地偏好排在前面的那篇评审。提示词还包含具体指令，以抵消冗长偏差（不因篇幅而非实质给予奖励）、自信偏差（不因断言性措辞而非恰当的保留给予奖励）、权威偏差（不因术语或引用数量而非准确性给予奖励）以及宽容偏差（使用完整的 1-6 评分区间，而非聚集在中间）。两篇评审被中性地标记为“Review A”和“Review B”，而非“参考”和“生成”，以防止基于来源的评分。",
  compareJudgeSystemPromptLabel: "系统提示词",
  compareJudgeUserPromptLabel: "用户提示词（论文 + 评审在运行时注入）",
  compareVsMid: " vs ",
  compareScoreOutOf: "/5",
  compareMetricCoverage: "覆盖度",
  compareMetricSpecificity: "针对性",
  compareMetricDepth: "深度",
  compareJumpTo: "跳转到",
  compareSectionOverallFeedback: "总体反馈",
  compareSectionDetailedComments: "详细评论",
  compareVisitPrefix: "访问 ",
  comparePdfReviewSuffix: " 评审",
  comparePdfFallback: "如果 iframe 未渲染，请下载 PDF ↓",
};
