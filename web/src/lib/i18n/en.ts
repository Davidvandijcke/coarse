// Canonical English message catalog for the website chrome (submit page +
// shared chrome). This is the single source of truth for message keys and the
// `Messages` type (see ../i18n.ts). Other locale catalogs mirror these keys.
//
// VALUES here are byte-identical to the literals previously hardcoded in the
// components — translating them is out of scope for this file. Strings that
// embed JSX (links, <em>, <strong>, <SplitFlap/>) or runtime values are split
// into static fragments (…Prefix/…Suffix/…Mid) so the surrounding markup and
// interpolation stay in the component.
//
// `as const` keeps the value types precise so `Messages = typeof en` is a
// closed key set: a missing or misspelled `t("key")` is a compile error.

export const en = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "Site language",

  // copy-to-clipboard code block
  codeBlockCopied: "copied ✓",
  codeBlockCopy: "copy",

  // header
  headerTagline: "peer review is a public good.",
  navSetup: "setup",
  navSideBySide: "side-by-side",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "Submissions are temporarily paused.",
  bannerBusyPrefix: "The system is busy (",
  bannerBusySuffix: " slots in use). Your review may be queued.",
  bannerFasterPrefix: "For faster results, try the CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "Hey ",
  heroGreetingSuffix: " can you review this paper?",
  heroHeading: "‘coarse!",
  heroLede: "AI agents review your paper and write a referee report. You pay the API cost directly. No account.",
  heroManifesto:
    "Academic peer review runs on unpaid academic labor. Others decided to make a business out of that. We didn't like that.",

  // hero — score preview
  scoreVsOthers: "vs. other AI reviewers",
  statCostNum: "< $2*",
  statCostLabel: "per review",
  statCostFootnote: "*typically :)",
  statCommentsNum: "20+",
  statCommentsLabel: "detailed comments",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "open source",

  // hero — competitive comparison
  comparePrefix: "Blind-evaluated against",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Scores higher on coverage, specificity, and depth -- at a fraction of the cost.",
  compareLink: "See the side-by-side →",

  // submit form — section heading + paper field
  formSubmitHeading: "Submit a paper",
  fieldPaper: "Paper",
  dropzoneAriaLabel: "Upload your paper — drop a file or click to browse",
  dropzoneInputAriaLabel: "Choose a file to upload",
  dropzoneReplaceSuffix: " MB — click or drop to replace",
  dropzonePromptPrefix: "Drop your file here, or ",
  dropzoneBrowse: "browse",
  dropzoneMaxSize: "Up to 50 MB",

  // submit form — email field
  fieldEmail: "Email ",
  fieldEmailQualifier: "(for web review only)",
  emailPlaceholderUnavailable: "— unavailable —",
  emailPlaceholder: "you@university.edu",
  emailAriaLabel: "Email address",
  emailHelperDisabled:
    "Email delivery is temporarily down. Save your review key when you submit and check back in about an hour.",
  emailHelperPrefix: "We'll email you when it's done. Check your spam folder if you don't see it.",

  // submit form — OpenRouter key field
  fieldKey: "OpenRouter key",
  fieldKeyGetOne: "get one →",
  keyOrPaste: "— or paste a key —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter API key",
  keyHelper:
    "OAuth keys stay in this tab only and clear when you close it. Never saved on our servers.",

  // submit form — author notes
  fieldNotes: "Notes for the reviewer",
  fieldNotesOptional: "(optional)",
  notesPlaceholder:
    "e.g. please focus on the identification strategy in §3 — the data section is still a placeholder.",
  notesAriaLabel: "Optional notes to steer the reviewer",
  notesHelper: "Steer what the reviewer focuses on. Does not override the rubric.",

  // submit form — cost estimate
  costEstimating: "Estimating cost...",
  costEstimatePrefix: "Estimated API cost: $",
  costUnavailable: "Cost estimate unavailable for this model",

  // submit form — Turnstile failure block
  turnstileFailedLine1Prefix:
    "Our human check couldn't complete. Something is blocking or slowing ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — usually a strict browser privacy mode (such as Safari's tracking prevention or Firefox ETP strict), a content/ad blocker (Brave Shields, uBlock Origin on some lists), or a slow or filtered network.",
  turnstileFailedLine2Prefix: "Try reloading the page first. If it persists, allow ",
  turnstileFailedLine2Mid: " for ",
  turnstileFailedLine2Suffix:
    " (disable content blockers or relax privacy settings), or use a different browser. On a preview URL, the deployment may also need that hostname on the Cloudflare Turnstile widget allowlist.",
  turnstileFailedLine3Prefix: "Or run coarse locally with your own OpenRouter key: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  // submit form — buttons + handoff picker
  submitButton: "Review my paper",
  submitButtonBusy: "Submitting...",
  submitOr: "or",
  handoffButton: "Review with my subscription ▾",
  handoffButtonBusy: "Preparing...",

  // submit form — handoff progress messages
  handoffUploading: "Uploading paper...",
  handoffPreparing: "Preparing handoff...",

  // submit form — explanatory paragraphs
  explainReviewLabel: "Review my paper:",
  explainReviewBody:
    " OpenRouter handles everything end-to-end. File deleted after processing. Review key works for 90 days. Usually under $2.",
  explainSubscriptionLabel: "Review with my subscription:",
  explainSubscriptionPart1:
    "we hand you a shell command that runs the full coarse pipeline locally using ",
  explainSubscriptionYour: "your",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", or",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "subscription for the LLM reasoning.",
  explainSubscriptionPdf:
    "You only pay ~$0.10 for the local Mistral OCR step (with your own OpenRouter key); non-PDF uploads (.tex, .md, .docx, …) skip OCR and need no OpenRouter key.",
  explainSubscriptionNonPdf:
    "Your file is not a PDF, so it skips the Mistral OCR step entirely — the whole run is covered by your subscription, no OpenRouter key needed.",
  explainSubscriptionPart3: "Review shows up on this page when done.",
  explainDisclaimer:
    "Runs locally on your machine using your own Claude Code, Codex, or Gemini CLI account. coarse.ink does not receive or store your provider login, and your provider's terms, usage limits, and organization policies apply. coarse.ink is not affiliated with Anthropic, OpenAI, or Google.",

  // submit form — handoff result card
  handoffReviewWithPrefix: "Review with ",
  handoffModelLabel: "model",
  handoffEffortLabel: "effort",
  handoffPastePromptPrefix: "Paste this prompt into your ",
  handoffPastePromptSuffix: " terminal:",
  handoffRunHint:
    "The agent will refresh the coarse-review skill, run the full review locally, and take 10–25 minutes. Your provider login stays on your machine.",
  handoffKeyNeededPrefix:
    "Your OpenRouter key needs to be on your machine first — export ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: ", or put it in ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " or ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    ". We don't pass it through the browser because the handoff URL ends up in your agent's chat log. If it's missing, the agent will ask.",
  handoffKeyNotNeeded:
    "No OpenRouter key needed for this paper — it's not a PDF, so extraction runs locally without the Mistral OCR step.",
  handoffReviewUrlIntro: "When the review finishes, it will appear at:",
  handoffInstallPrefix: "Don't have ",
  handoffInstallSuffix: " yet? ",
  handoffInstallLink: "install it →",

  // retrieve
  findReviewHeading: "Find a review",
  findReviewPlaceholder: "Paste your review key, full review link, or legacy review ID...",
  findReviewAriaLabel: "Review key",
  findReviewButton: "Find",

  // footer
  footerPrivacy: "privacy",
  footerTerms: "terms",
  footerContact: "contact",

  // status / errors (set in handlers)
  noticeKeyMigrated:
    "Moved your saved OpenRouter key into tab-only storage. It will clear when you close this tab.",
  errorLoginNoPersist:
    "Logged in, but couldn't keep the key in this tab. You'll need to paste it again if this page reloads.",
  errorLoginFailed: "OpenRouter login failed. Please try again or paste a key manually.",
  errorAuthFailed:
    "Authentication failed. On preview deploys this usually means the browser's cached Basic Auth credentials didn't get sent on the form submit. Refresh the tab (Cmd/Ctrl+Shift+R), sign in again at the password prompt, and retry.",
  errorServiceUnavailable: "Service temporarily unavailable — please try again in a minute.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "Our human-check widget couldn't load — a browser extension (Brave Shields, uBlock Origin, Firefox ETP strict) is most likely blocking challenges.cloudflare.com. Try disabling it for ",
  errorTurnstileBlockedSuffix: ", or run coarse locally: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "Still waiting for the human check to load — give it a second and try again.",
  errorPrepareUpload: "Failed to prepare upload",
  errorUploadFailed: "File upload failed — please try again",
  errorSubmissionFailed: "Submission failed",
  errorHandoffFailed: "Handoff failed",
  launchCommandCopied: "Command copied to clipboard. Paste it into your terminal.",
  launchOpeningCodex: "Opening Codex desktop app — the composer should pre-fill. Hit send.",
  launchOpeningPrefix: "Opening ",
  launchOpeningSuffix: " — paste the prompt from your clipboard (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " desktop app didn't open. If you only have the CLI version installed, paste the commands above into your terminal instead.",
  errorLoginCouldNotStartPrefix: "OpenRouter login could not start: ",

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "Review language",
  reviewLanguageAuto: "Auto — match the paper's language",
  reviewLanguageHelper:
    "Defaults to the paper's own language; quotes always stay in the original.",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "Model",
  modelPickerUnavailableTitle: "Currently unavailable",
  modelPickerSearchPlaceholder: "Search models...",
  modelPickerLoading: "Loading models...",
  modelPickerNoResults: "No models found.",
  modelPickerSearch: "search models...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "Connected to OpenRouter",
  openRouterLogOut: "Log out",
  openRouterLogIn: "Log in with OpenRouter →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "This review needs the full secure review link or review key.",
  statusLoadFailed: "Failed to load the review status. Please try again.",
  statusCancelledByUser: "Review cancelled by user",
  statusLoading: "Loading",
  statusAccessTokenRequired: "Access token required.",
  statusNotFoundHeading: "Review not found.",
  statusNotFoundBody: "Check the review key and try again.",
  statusCancelConfirmHeading: "Cancel review?",
  statusCancelConfirmBody: "Are you sure? You will not be able to see your results.",
  statusCancelling: "Cancelling...",
  statusYesCancel: "Yes, cancel",
  statusGoBack: "Go back",
  statusLabelCancelled: "cancelled",
  statusLabelFailed: "failed",
  statusLabelReviewing: "reviewing",
  statusLabelQueued: "queued",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "Reading your paper.",
  statusQueuedHeading: "Queued.",
  statusRunningBody: "Running the review pipeline (usually 30–60 minutes).",
  statusQueuedBody: "Your review is queued and will start shortly.",
  statusEmailWhenDone: "We'll email you when it's done.",
  statusCancelledHeading: "Review cancelled.",
  statusCancelledBody:
    "The queued job was marked cancelled. If work had already started, the worker may take a little time to wind down.",
  statusFailedHeading: "Failed.",
  statusUnexpectedError: "An unexpected error occurred.",
  statusResubmitPrefix: "Please try resubmitting, or post your issue on the ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: ".",
  statusTryAgain: "Try again →",
  statusKeyBoxSave: "Your review key — save this",
  statusKeyBoxLegacy: "Legacy review link",
  statusCopied: "Copied",
  statusCopyLink: "Copy link",
  statusRedirectNote: "This page will redirect automatically when your review is ready.",
  statusCancelReview: "Cancel review",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "This review needs the full secure review link or review key.",
  reviewClientLoadFailed: "Failed to load the review. Please try again.",
  reviewClientLoading: "Loading",
  reviewClientNotFoundHeading: "Review not found.",
  reviewClientNotFoundBody: "Check your key and try again.",
  reviewClientSubmitNewPaper: "Submit a new paper →",
  reviewClientAccessTokenRequired: "Access token required.",
  reviewClientBackHome: "Back home →",
  reviewClientReadingHeading: "Reading your paper.",
  reviewClientQueuedHeading: "Queued.",
  reviewClientRunningBody: "Usually 30–60 minutes. This page updates automatically.",
  reviewClientQueuedBody: "Processing begins shortly.",
  reviewClientFailedHeading: "Review failed.",
  reviewClientUnexpectedError: "An unexpected error occurred.",
  reviewClientTryAgain: "Try again →",
  reviewClientCancelledHeading: "Review cancelled.",
  reviewClientCancelledBody: "This review was cancelled before completion.",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "Show less",
  reviewShowMore: "Show more",
  reviewShowInPaper: "Show in paper",
  reviewMarkActive: "Mark as active",
  reviewMarkDone: "Mark as done",
  reviewDismiss: "Dismiss",
  reviewDiscuss: "Discuss",
  reviewDiscussTitle: "Discuss this comment with an AI model",
  reviewShowDetails: "Show details",
  reviewStatusDone: "Done",
  reviewStatusDismissed: "Dismissed",
  reviewHide: "Hide",
  reviewFilterAll: "All",
  reviewFilterActive: "Active",
  reviewFilterDone: "Done",
  reviewFilterDismissed: "Dismissed",
  reviewSidebarOverallFeedback: "Overall Feedback",
  reviewSidebarCommentsPrefix: "Comments (",
  reviewSidebarCommentsRemainingSuffix: " remaining)",
  reviewRemainingSuffix: " remaining",
  reviewDownload: "Download",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "Print / PDF",
  reviewHidePaper: "Hide Paper",
  reviewShowPaper: "Show Paper",
  reviewCopied: "Copied",
  reviewShare: "Share",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "Drag to resize the paper panel",
  reviewResizeTitle: "Drag to resize",
  reviewOfPrefix: "Review of ",
  reviewMetaModel: "Model",
  reviewMetaDate: "Date",
  reviewMetaDomain: "Domain",
  reviewMetaTime: "Time",
  reviewMetaCost: "Cost",
  reviewMetaReviewLanguage: "Review language",
  reviewMetaAutoDetectedSuffix: " · auto-detected",
  reviewOverallFeedbackHeading: "Overall Feedback",
  reviewDetailedCommentsPrefix: "Detailed Comments (",
  reviewDetailedCommentsSuffix: ")",
  reviewGeneratedByPrefix: "Generated by ",
  reviewGeneratedBySuffix: ". Of course.",
  reviewShareThisReview: "Share this review",
  reviewDeleteReview: "Delete review",
  reviewDeleteConfirmHeading: "Delete review?",
  reviewDeleteConfirmBody: "Are you sure? You will not be able to see your results.",
  reviewDeleting: "Deleting...",
  reviewYesDelete: "Yes, delete",
  reviewGoBack: "Go back",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "Is this critique actually correct?",
  chatExamplePrompt2: "How should I revise to address it?",
  chatExamplePrompt3: "Where in the paper does this apply?",
  chatNoResponse: "No response from the model. Try again or switch models.",
  chatSessionExpired: "Your OpenRouter session expired. Log in again to continue.",
  chatSomethingWrong: "Something went wrong.",
  chatDiscussKicker: "Discuss · ",
  chatKickerComment: "comment #",
  chatKickerOverallFeedback: "overall feedback",
  chatDiscussAriaPrefix: "Discuss: ",
  chatCloseAriaLabel: "Close chat",
  chatDisconnectKeyTitle:
    "Disconnect your OpenRouter key (it isn't stored beyond this tab)",
  chatDisconnectKey: "Disconnect key",
  chatInputPlaceholder: "Ask about this comment…",
  chatMessageAriaLabel: "Message",
  chatStop: "Stop",
  chatSend: "Send",
  chatModelDisclosurePrefix: "Model: ",
  chatKeyGateIntro:
    "Connect OpenRouter to chat about this comment. Your key is sent straight to OpenRouter — never to our servers — and clears when you close this tab.",
  chatKeyGateOrPaste: "— or paste a key —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "OpenRouter API key",
  chatKeyGateUseKey: "Use key",
  chatKeyGateHelper:
    "OAuth keys stay in this tab only and clear when you close it. Never saved on our servers.",
  chatEmptyHintPrefix: "Ask anything about this comment. Each message sends ",
  chatEmptyHintFullPaper: "the full paper",
  chatEmptyHintQuotedPassage: "the quoted passage and feedback",
  chatEmptyHintSuffix: " as context and runs on your OpenRouter credits.",
  chatEmptyHintNoPaper:
    "The full paper text isn't stored for this review, so answers rely on the quoted passage and feedback only.",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "Opened ",
  handoffMenuOpenedPromptMid: " with the prompt prefilled — attach coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md, then send. (Prompt also copied, just in case.)",
  handoffMenuOpenedPlainMid: " — attach coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md and paste the copied prompt.",
  handoffMenuButtonTitle:
    "Send the paper + review to your own AI chat (Claude, ChatGPT, Gemini, Grok, DeepSeek)",
  handoffMenuButton: "Discuss with your AI",
  handoffMenuDownloadsIntro: "Downloads the paper + review, then opens:",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "Paper",
  paperPanelDownload: "Download",
  paperPanelDownloadAriaLabel: "Download paper markdown",
  paperPanelCloseAriaLabel: "Close paper panel",
} as const;
