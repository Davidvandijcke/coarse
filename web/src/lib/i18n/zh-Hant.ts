// Traditional Chinese (zh-Hant) site-UI catalog. Mirrors the keys of ./en.ts
// exactly; only the values are translated. Brand/technical tokens (coarse,
// OpenRouter, Claude Code, Codex, Gemini CLI, commands, URLs, model IDs) and
// glyphs are kept verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix
// fragments are significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const zhHant: Messages = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "網站語言",

  // copy-to-clipboard code block
  codeBlockCopied: "已複製 ✓",
  codeBlockCopy: "複製",

  // header
  headerTagline: "同儕審查是一種公共財。",
  navSetup: "設定",
  navSideBySide: "並列比較",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "投稿暫時停止。",
  bannerBusyPrefix: "系統忙碌中（",
  bannerBusySuffix: " 個名額使用中）。您的審查可能需要排隊。",
  bannerFasterPrefix: "想要更快的結果，請改用 CLI：",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "嘿 ",
  heroGreetingSuffix: " 你可以幫忙審查這篇論文嗎？",
  heroHeading: "‘coarse!",
  heroLede:
    "AI 代理人審查您的論文並撰寫審稿報告。API 費用由您直接支付。無需帳號。",
  heroManifesto:
    "學術同儕審查仰賴未支薪的學術勞動。有些人決定把這當成生意來經營。我們並不認同。",

  // hero — score preview
  scoreVsOthers: "對比其他 AI 審查工具",
  statCostNum: "< $2*",
  statCostLabel: "每次審查",
  statCostFootnote: "*通常如此 :)",
  statCommentsNum: "20+",
  statCommentsLabel: "詳細意見",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "開放原始碼",

  // hero — competitive comparison
  comparePrefix: "盲測評比對象",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "在涵蓋度、具體性與深度上得分更高——而成本只是其中的一小部分。",
  compareLink: "查看並列比較 →",

  // submit form — section heading + paper field
  formSubmitHeading: "提交論文",
  fieldPaper: "論文",
  dropzoneAriaLabel: "上傳您的論文——拖曳檔案或點擊瀏覽",
  dropzoneInputAriaLabel: "選擇要上傳的檔案",
  dropzoneReplaceSuffix: " MB——點擊或拖曳以替換",
  dropzonePromptPrefix: "將檔案拖曳到這裡，或 ",
  dropzoneBrowse: "瀏覽",
  dropzoneMaxSize: "最大 50 MB",

  // submit form — email field
  fieldEmail: "電子郵件 ",
  fieldEmailQualifier: "（僅用於網頁審查）",
  emailPlaceholderUnavailable: "— 無法使用 —",
  emailPlaceholder: "you@university.edu",
  emailAriaLabel: "電子郵件地址",
  emailHelperDisabled:
    "電子郵件寄送暫時停擺。提交時請儲存您的審查金鑰，並在大約一小時後回來查看。",
  emailHelperPrefix: "完成後我們會以電子郵件通知您。若沒看到，請檢查垃圾郵件匣。",

  // submit form — OpenRouter key field
  fieldKey: "OpenRouter 金鑰",
  fieldKeyGetOne: "前往取得 →",
  keyOrPaste: "— 或貼上金鑰 —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter API 金鑰",
  keyHelper:
    "OAuth 金鑰只會保留在此分頁，並在您關閉分頁時清除。絕不會儲存在我們的伺服器上。",

  // submit form — author notes
  fieldNotes: "給審查者的備註",
  fieldNotesOptional: "（選填）",
  notesPlaceholder:
    "例如：請聚焦於 §3 的辨識策略——資料章節目前仍是佔位內容。",
  notesAriaLabel: "用以引導審查者的選填備註",
  notesHelper: "引導審查者關注的重點。不會覆寫評分準則。",

  // submit form — cost estimate
  costEstimating: "估算費用中...",
  costEstimatePrefix: "預估 API 費用：$",
  costUnavailable: "此模型無法提供費用估算",

  // submit form — Turnstile failure block
  turnstileFailedLine1Prefix:
    "我們的真人驗證無法完成。有東西正在阻擋或拖慢 ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — 通常是瀏覽器的嚴格隱私模式（例如 Safari 的追蹤防護或 Firefox ETP 嚴格模式）、內容／廣告攔截器（Brave Shields、某些清單上的 uBlock Origin），或是速度緩慢或遭過濾的網路。",
  turnstileFailedLine2Prefix: "請先嘗試重新載入頁面。若問題持續，請允許 ",
  turnstileFailedLine2Mid: " 用於 ",
  turnstileFailedLine2Suffix:
    " （停用內容攔截器或放寬隱私設定），或改用其他瀏覽器。在預覽 URL 上，該部署可能還需要將此主機名稱加入 Cloudflare Turnstile 小工具的允許清單。",
  turnstileFailedLine3Prefix: "或使用您自己的 OpenRouter 金鑰在本機執行 coarse： ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: "。",

  // submit form — buttons + handoff picker
  submitButton: "審查我的論文",
  submitButtonBusy: "提交中...",
  submitOr: "或",
  handoffButton: "用我的訂閱審查 ▾",
  handoffButtonBusy: "準備中...",

  // submit form — handoff progress messages
  handoffUploading: "上傳論文中...",
  handoffPreparing: "準備交接中...",

  // submit form — explanatory paragraphs
  explainReviewLabel: "審查我的論文：",
  explainReviewBody:
    " OpenRouter 從頭到尾全程處理。處理完成後即刪除檔案。審查金鑰有效 90 天。通常低於 $2。",
  explainSubscriptionLabel: "用我的訂閱審查：",
  explainSubscriptionPart1:
    "我們給您一段 shell 指令，使用 ",
  explainSubscriptionYour: "您自己的",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: "、",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: "，或",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "訂閱進行 LLM 推理，在本機執行完整的 coarse 流程。",
  explainSubscriptionPdf:
    "您只需為本機的 Mistral OCR 步驟支付約 ~$0.10（使用您自己的 OpenRouter 金鑰）；非 PDF 上傳（.tex, .md, .docx, …）會略過 OCR，無需 OpenRouter 金鑰。",
  explainSubscriptionNonPdf:
    "您的檔案不是 PDF，因此會完全略過 Mistral OCR 步驟——整個執行過程由您的訂閱涵蓋，無需 OpenRouter 金鑰。",
  explainSubscriptionPart3: "完成後審查會顯示在此頁面。",
  explainDisclaimer:
    "在您自己的機器上使用您自己的 Claude Code、Codex 或 Gemini CLI 帳號於本機執行。coarse.ink 不會接收或儲存您的供應商登入資訊，且您供應商的條款、使用限制與組織政策均適用。coarse.ink 與 Anthropic、OpenAI 或 Google 並無任何隸屬關係。",

  // submit form — handoff result card
  handoffReviewWithPrefix: "使用 ",
  handoffModelLabel: "模型",
  handoffEffortLabel: "推理強度",
  handoffPastePromptPrefix: "將此提示貼到您的 ",
  handoffPastePromptSuffix: " 終端機：",
  handoffRunHint:
    "代理人會重新整理 coarse-review 技能，在本機執行完整審查，需時 10–25 分鐘。您的供應商登入資訊會留在您的機器上。",
  handoffKeyNeededPrefix:
    "您的 OpenRouter 金鑰必須先放在您的機器上——請匯出 ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: "，或將其放入 ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " 或 ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    "。我們不會透過瀏覽器傳遞它，因為交接 URL 會出現在您代理人的對話記錄中。若缺少它，代理人會主動詢問。",
  handoffKeyNotNeeded:
    "這篇論文無需 OpenRouter 金鑰——它不是 PDF，因此擷取會在本機執行，不經過 Mistral OCR 步驟。",
  handoffReviewUrlIntro: "審查完成後，會出現在：",
  handoffInstallPrefix: "還沒有 ",
  handoffInstallSuffix: " 嗎？ ",
  handoffInstallLink: "立即安裝 →",

  // retrieve
  findReviewHeading: "尋找審查",
  findReviewPlaceholder: "貼上您的審查金鑰、完整審查連結或舊版審查 ID...",
  findReviewAriaLabel: "審查金鑰",
  findReviewButton: "尋找",

  // footer
  footerPrivacy: "隱私權",
  footerTerms: "條款",
  footerContact: "聯絡我們",

  // status / errors (set in handlers)
  noticeKeyMigrated:
    "已將您儲存的 OpenRouter 金鑰移至僅限此分頁的儲存空間。關閉此分頁時它會被清除。",
  errorLoginNoPersist:
    "已登入，但無法將金鑰保留在此分頁。若此頁面重新載入，您需要再次貼上金鑰。",
  errorLoginFailed: "OpenRouter 登入失敗。請再試一次，或手動貼上金鑰。",
  errorAuthFailed:
    "驗證失敗。在預覽部署上，這通常表示瀏覽器快取的 Basic Auth 憑證在表單提交時未被送出。請重新整理分頁（Cmd/Ctrl+Shift+R），在密碼提示處重新登入，然後再試一次。",
  errorServiceUnavailable: "服務暫時無法使用——請於一分鐘後再試一次。",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "我們的真人驗證小工具無法載入——很可能是瀏覽器擴充功能（Brave Shields、uBlock Origin、Firefox ETP 嚴格模式）正在阻擋 challenges.cloudflare.com。請嘗試為以下對象停用它： ",
  errorTurnstileBlockedSuffix: "，或在本機執行 coarse：uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "仍在等待真人驗證載入——請稍候片刻再試一次。",
  errorPrepareUpload: "準備上傳失敗",
  errorUploadFailed: "檔案上傳失敗——請再試一次",
  errorSubmissionFailed: "提交失敗",
  errorHandoffFailed: "交接失敗",
  launchCommandCopied: "指令已複製到剪貼簿。請將它貼到您的終端機。",
  launchOpeningCodex: "正在開啟 Codex 桌面應用程式——編輯器應已預先填入。請按送出。",
  launchOpeningPrefix: "正在開啟 ",
  launchOpeningSuffix: " — 請從剪貼簿貼上提示（⌘V / Ctrl+V）。",
  launchDidntOpenSuffix:
    " 桌面應用程式未開啟。若您只安裝了 CLI 版本，請改將上述指令貼到您的終端機。",
  errorLoginCouldNotStartPrefix: "OpenRouter 登入無法啟動： ",

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "審查語言",
  reviewLanguageAuto: "自動——比照論文的語言",
  reviewLanguageHelper:
    "預設使用論文本身的語言；引文一律保留原文。",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "模型",
  modelPickerUnavailableTitle: "目前無法使用",
  modelPickerSearchPlaceholder: "搜尋模型...",
  modelPickerLoading: "載入模型中...",
  modelPickerNoResults: "找不到模型。",
  modelPickerSearch: "搜尋模型...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "已連線至 OpenRouter",
  openRouterLogOut: "登出",
  openRouterLogIn: "使用 OpenRouter 登入 →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "此審查需要完整的安全審查連結或審查金鑰。",
  statusLoadFailed: "載入審查狀態失敗。請再試一次。",
  statusCancelledByUser: "審查已由使用者取消",
  statusLoading: "載入中",
  statusAccessTokenRequired: "需要存取權杖。",
  statusNotFoundHeading: "找不到審查。",
  statusNotFoundBody: "請檢查審查金鑰後再試一次。",
  statusCancelConfirmHeading: "取消審查？",
  statusCancelConfirmBody: "您確定嗎？您將無法看到您的結果。",
  statusCancelling: "取消中...",
  statusYesCancel: "是，取消",
  statusGoBack: "返回",
  statusLabelCancelled: "已取消",
  statusLabelFailed: "失敗",
  statusLabelReviewing: "審查中",
  statusLabelQueued: "排隊中",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "正在閱讀您的論文。",
  statusQueuedHeading: "排隊中。",
  statusRunningBody: "正在執行審查流程（通常需 30–60 分鐘）。",
  statusQueuedBody: "您的審查已排入佇列，即將開始。",
  statusEmailWhenDone: "完成後我們會以電子郵件通知您。",
  statusCancelledHeading: "審查已取消。",
  statusCancelledBody:
    "排隊中的工作已標記為取消。若作業已經開始，工作程序可能需要一些時間才能結束。",
  statusFailedHeading: "失敗。",
  statusUnexpectedError: "發生未預期的錯誤。",
  statusResubmitPrefix: "請嘗試重新提交，或將您的問題張貼到 ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: "。",
  statusTryAgain: "再試一次 →",
  statusKeyBoxSave: "您的審查金鑰——請妥善保存",
  statusKeyBoxLegacy: "舊版審查連結",
  statusCopied: "已複製",
  statusCopyLink: "複製連結",
  statusRedirectNote: "您的審查就緒後，此頁面會自動跳轉。",
  statusCancelReview: "取消審查",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "此審查需要完整的安全審查連結或審查金鑰。",
  reviewClientLoadFailed: "載入審查失敗。請再試一次。",
  reviewClientLoading: "載入中",
  reviewClientNotFoundHeading: "找不到審查。",
  reviewClientNotFoundBody: "請檢查您的金鑰後再試一次。",
  reviewClientSubmitNewPaper: "提交新論文 →",
  reviewClientAccessTokenRequired: "需要存取權杖。",
  reviewClientBackHome: "返回首頁 →",
  reviewClientReadingHeading: "正在閱讀您的論文。",
  reviewClientQueuedHeading: "排隊中。",
  reviewClientRunningBody: "通常需 30–60 分鐘。此頁面會自動更新。",
  reviewClientQueuedBody: "即將開始處理。",
  reviewClientFailedHeading: "審查失敗。",
  reviewClientUnexpectedError: "發生未預期的錯誤。",
  reviewClientTryAgain: "再試一次 →",
  reviewClientCancelledHeading: "審查已取消。",
  reviewClientCancelledBody: "此審查在完成前已被取消。",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "顯示較少",
  reviewShowMore: "顯示更多",
  reviewShowInPaper: "在論文中顯示",
  reviewMarkActive: "標記為進行中",
  reviewMarkDone: "標記為已完成",
  reviewDismiss: "忽略",
  reviewDiscuss: "討論",
  reviewDiscussTitle: "與 AI 模型討論這則意見",
  reviewShowDetails: "顯示詳情",
  reviewStatusDone: "已完成",
  reviewStatusDismissed: "已忽略",
  reviewHide: "隱藏",
  reviewFilterAll: "全部",
  reviewFilterActive: "進行中",
  reviewFilterDone: "已完成",
  reviewFilterDismissed: "已忽略",
  reviewSidebarOverallFeedback: "整體回饋",
  reviewSidebarCommentsPrefix: "意見（",
  reviewSidebarCommentsRemainingSuffix: " 則待處理）",
  reviewRemainingSuffix: " 則待處理",
  reviewDownload: "下載",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "列印 / PDF",
  reviewHidePaper: "隱藏論文",
  reviewShowPaper: "顯示論文",
  reviewCopied: "已複製",
  reviewShare: "分享",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "拖曳以調整論文面板大小",
  reviewResizeTitle: "拖曳以調整大小",
  reviewOfPrefix: "審查報告：",
  reviewMetaModel: "模型",
  reviewMetaDate: "日期",
  reviewMetaDomain: "領域",
  reviewMetaTime: "耗時",
  reviewMetaCost: "費用",
  reviewMetaReviewLanguage: "審查語言",
  reviewMetaAutoDetectedSuffix: " · 自動偵測",
  reviewOverallFeedbackHeading: "整體回饋",
  reviewDetailedCommentsPrefix: "詳細意見（",
  reviewDetailedCommentsSuffix: "）",
  reviewGeneratedByPrefix: "由 ",
  reviewGeneratedBySuffix: " 生成。當然。",
  reviewShareThisReview: "分享這則審查",
  reviewDeleteReview: "刪除審查",
  reviewDeleteConfirmHeading: "刪除審查？",
  reviewDeleteConfirmBody: "您確定嗎？您將無法看到您的結果。",
  reviewDeleting: "刪除中...",
  reviewYesDelete: "是，刪除",
  reviewGoBack: "返回",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "這則批評真的正確嗎？",
  chatExamplePrompt2: "我該如何修改才能回應它？",
  chatExamplePrompt3: "論文中的哪個部分與此相關？",
  chatNoResponse: "模型沒有回應。請再試一次或更換模型。",
  chatSessionExpired: "您的 OpenRouter 工作階段已過期。請重新登入以繼續。",
  chatSomethingWrong: "發生錯誤。",
  chatDiscussKicker: "討論 · ",
  chatKickerComment: "意見 #",
  chatKickerOverallFeedback: "整體回饋",
  chatDiscussAriaPrefix: "討論： ",
  chatCloseAriaLabel: "關閉聊天",
  chatDisconnectKeyTitle:
    "中斷您的 OpenRouter 金鑰（它不會在此分頁以外被儲存）",
  chatDisconnectKey: "中斷金鑰",
  chatInputPlaceholder: "詢問關於這則意見的問題…",
  chatMessageAriaLabel: "訊息",
  chatStop: "停止",
  chatSend: "送出",
  chatModelDisclosurePrefix: "模型： ",
  chatKeyGateIntro:
    "連線 OpenRouter 即可討論這則意見。您的金鑰會直接送往 OpenRouter——絕不會送到我們的伺服器——並在您關閉此分頁時清除。",
  chatKeyGateOrPaste: "— 或貼上金鑰 —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "OpenRouter API 金鑰",
  chatKeyGateUseKey: "使用金鑰",
  chatKeyGateHelper:
    "OAuth 金鑰只會保留在此分頁，並在您關閉分頁時清除。絕不會儲存在我們的伺服器上。",
  chatEmptyHintPrefix: "歡迎詢問任何關於這則意見的問題。每則訊息都會將 ",
  chatEmptyHintFullPaper: "整篇論文",
  chatEmptyHintQuotedPassage: "引用的段落與回饋",
  chatEmptyHintSuffix: " 作為上下文一併送出，並使用您的 OpenRouter 額度執行。",
  chatEmptyHintNoPaper:
    "此審查未儲存完整的論文文字，因此回答僅依據引用的段落與回饋。",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "已開啟 ",
  handoffMenuOpenedPromptMid: " 並預先填入提示——請附上 coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md，然後送出。（提示也已複製，以防萬一。）",
  handoffMenuOpenedPlainMid: " — 請附上 coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md 並貼上已複製的提示。",
  handoffMenuButtonTitle:
    "將論文與審查傳送到您自己的 AI 聊天工具（Claude、ChatGPT、Gemini、Grok、DeepSeek）",
  handoffMenuButton: "與您的 AI 討論",
  handoffMenuDownloadsIntro: "下載論文與審查，然後開啟：",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "論文",
  paperPanelDownload: "下載",
  paperPanelDownloadAriaLabel: "下載論文 markdown",
  paperPanelCloseAriaLabel: "關閉論文面板",
};
