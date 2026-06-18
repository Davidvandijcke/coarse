// Simplified Chinese (zh-Hans) site-UI catalog. Mirrors the keys of ./en.ts
// exactly; only the values are translated. Brand/technical tokens (coarse,
// OpenRouter, Claude Code, Codex, Gemini CLI, commands, URLs, model IDs) and
// glyphs are kept verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix
// fragments are significant and match en.ts (they concatenate with English
// brand tokens and runtime values).

import type { Messages } from "@/lib/i18n";

export const zhHans: Messages = {
  siteLanguageLabel: "网站语言",

  codeBlockCopied: "已复制 ✓",
  codeBlockCopy: "复制",

  headerTagline: "同行评审是一种公共产品。",
  navSetup: "设置",
  navSideBySide: "并排对比",
  navGithub: "github ↗",

  bannerPausedDefault: "投稿已暂时暂停。",
  bannerBusyPrefix: "系统繁忙（",
  bannerBusySuffix: " 个名额正在使用中）。你的评审可能会进入队列。",
  bannerFasterPrefix: "想要更快的结果，试试 CLI：",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "嘿 ",
  heroGreetingSuffix: " 能帮我评审这篇论文吗？",
  heroHeading: "‘coarse!",
  heroLede:
    "AI 智能体评审你的论文并撰写审稿报告。你直接支付 API 费用。无需账户。",
  heroManifesto:
    "学术同行评审依靠无偿的学术劳动运转。有些人却决定借此牟利。我们对此并不认同。",

  scoreVsOthers: "对比其他 AI 评审工具",
  statCostNum: "< $2*",
  statCostLabel: "每次评审",
  statCostFootnote: "*通常情况下 :)",
  statCommentsNum: "20+",
  statCommentsLabel: "条详细评论",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "开源",

  comparePrefix: "盲测对比",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "在覆盖度、针对性和深度上得分更高——而成本只是其中的一小部分。",
  compareLink: "查看并排对比 →",

  formSubmitHeading: "提交论文",
  fieldPaper: "论文",
  dropzoneAriaLabel: "上传你的论文——拖入文件或点击浏览",
  dropzoneInputAriaLabel: "选择要上传的文件",
  dropzoneReplaceSuffix: " MB——点击或拖入以替换",
  dropzonePromptPrefix: "将文件拖到这里，或者 ",
  dropzoneBrowse: "浏览",
  dropzoneMaxSize: "最大 50 MB",

  fieldEmail: "电子邮箱 ",
  fieldEmailQualifier: "（仅用于网页评审）",
  emailPlaceholderUnavailable: "— 不可用 —",
  emailPlaceholder: "you@university.edu",
  emailAriaLabel: "电子邮箱地址",
  emailHelperDisabled:
    "邮件投递暂时中断。提交时请保存好你的评审密钥，大约一小时后再回来查看。",
  emailHelperPrefix:
    "完成后我们会通过邮件通知你。如果没有收到，请检查你的垃圾邮件文件夹。",

  fieldKey: "OpenRouter 密钥",
  fieldKeyGetOne: "获取一个 →",
  keyOrPaste: "— 或粘贴一个密钥 —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter API 密钥",
  keyHelper:
    "OAuth 密钥仅保留在此标签页中，关闭后即清除。绝不会保存在我们的服务器上。",

  fieldNotes: "给评审者的备注",
  fieldNotesOptional: "（可选）",
  notesPlaceholder:
    "例如：请重点关注 §3 中的识别策略——数据部分目前仍是占位内容。",
  notesAriaLabel: "用于引导评审者的可选备注",
  notesHelper: "引导评审者的关注重点。不会覆盖评审标准。",

  costEstimating: "正在估算费用...",
  costEstimatePrefix: "预计 API 费用：$",
  costUnavailable: "无法估算该模型的费用",

  turnstileFailedLine1Prefix:
    "我们的人机验证无法完成。有什么东西在阻止或拖慢 ",
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

  submitButton: "评审我的论文",
  submitButtonBusy: "正在提交...",
  submitOr: "或",
  handoffButton: "用我的订阅来评审 ▾",
  handoffButtonBusy: "正在准备...",

  handoffUploading: "正在上传论文...",
  handoffPreparing: "正在准备交接...",

  explainReviewLabel: "评审我的论文：",
  explainReviewBody:
    " OpenRouter 全程处理一切。文件在处理后即被删除。评审密钥有效期为 90 天。通常不到 $2。",
  explainSubscriptionLabel: "用我的订阅来评审：",
  explainSubscriptionPart1:
    "我们会给你一条 shell 命令，使用 ",
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
    "使用你自己的 Claude Code、Codex 或 Gemini CLI 账户在你本地的机器上运行。coarse.ink 不会接收或存储你的提供商登录信息，并且你的提供商的条款、使用限额和组织政策均适用。coarse.ink 与 Anthropic、OpenAI 或 Google 无任何关联。",

  handoffReviewWithPrefix: "用 ",
  handoffModelLabel: "模型",
  handoffEffortLabel: "强度",
  handoffPastePromptPrefix: "将这段提示词粘贴到你的 ",
  handoffPastePromptSuffix: " 终端中：",
  handoffRunHint:
    "智能体会刷新 coarse-review 技能，在本地运行完整评审，耗时 10–25 分钟。你的提供商登录信息会保留在你的机器上。",
  handoffKeyNeededPrefix:
    "你的 OpenRouter 密钥需要先放在你的机器上——请导出 ",
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

  findReviewHeading: "查找评审",
  findReviewPlaceholder: "粘贴你的评审密钥、完整评审链接或旧版评审 ID...",
  findReviewAriaLabel: "评审密钥",
  findReviewButton: "查找",

  footerPrivacy: "隐私",
  footerTerms: "条款",
  footerContact: "联系",

  noticeKeyMigrated:
    "已将你保存的 OpenRouter 密钥移入仅限本标签页的存储。关闭此标签页时它将被清除。",
  errorLoginNoPersist:
    "已登录，但无法在本标签页中保留密钥。如果此页面重新加载，你需要再次粘贴它。",
  errorLoginFailed:
    "OpenRouter 登录失败。请重试或手动粘贴一个密钥。",
  errorAuthFailed:
    "身份验证失败。在预览部署上，这通常意味着浏览器缓存的 Basic Auth 凭据在提交表单时没有被发送。请刷新标签页（Cmd/Ctrl+Shift+R），在密码提示处重新登录，然后重试。",
  errorServiceUnavailable: "服务暂时不可用——请一分钟后重试。",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "我们的人机验证小组件无法加载——很可能是浏览器扩展（Brave Shields、uBlock Origin、Firefox ETP 严格模式）拦截了 challenges.cloudflare.com。请尝试为以下对象停用它： ",
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
  launchOpeningSuffix: " ——从剪贴板粘贴提示词（⌘V / Ctrl+V）。",
  launchDidntOpenSuffix:
    " 桌面应用未能打开。如果你只安装了 CLI 版本，请改为将上面的命令粘贴到你的终端中。",
  errorLoginCouldNotStartPrefix: "OpenRouter 登录无法启动： ",

  reviewLanguageLabel: "评审语言",
  reviewLanguageAuto: "自动——匹配论文的语言",
  reviewLanguageHelper:
    "默认使用论文本身的语言；引文始终保留原文。",
};
