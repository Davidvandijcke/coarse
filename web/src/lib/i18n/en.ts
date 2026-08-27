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
  deepLiteratureLabel: "Deep literature search",
  deepLiteratureHelper:
    "Uses Perplexity Sonar Deep Research for a more exhaustive, multi-step source search. Usually adds a few minutes and about $0.30 to the estimate.",
  deepLiteratureOn: "On",
  deepLiteratureOff: "Off",

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
    "PDF processing uses your OpenRouter key for local Mistral OCR and a small vision-QA charge when that check runs; non-PDF uploads (.tex, .md, .docx, …) skip OCR and need no OpenRouter key.",
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

  // setup page (setup/page.tsx)
  // setup page — tab switcher
  setupTablistAriaLabel: "Setup path",
  setupTabOpenRouter: "OpenRouter key",
  setupTabSubscription: "Use my subscription",
  // setup page — OpenRouter tab intro
  setupOrHeading: "Get your OpenRouter key",
  setupOrIntro:
    "Takes about 2 minutes. You'll need a credit card for ~$1 in credits to get started — you'll top up to $20 in step 2.",
  setupOrFasterLabel: "Faster option:",
  setupOrFasterMid1: " on the main form you can click ",
  setupOrFasterLogIn: "“Log in with OpenRouter”",
  setupOrFasterSuffix:
    " to authorize coarse and skip manual key creation. You still need an OpenRouter account with credits (steps 1 and 2 below), and we still recommend setting a per-key spend limit (step 4).",
  // setup page — OpenRouter step 1
  setupOrStep1Title: "Create an account",
  setupOrStep1BodyPrefix: "Go to ",
  setupOrStep1BodySuffix: " and click “Get API Key” or sign up with Google / GitHub.",
  setupOrStep1Annotation: "homepage",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "A unified API for LLMs — one key, many models.",
  // setup page — OpenRouter step 2
  setupOrStep2Title: "Add credits",
  setupOrStep2BodyPrefix: "Navigate to ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    ". Add at least $20. Cheap open-source models cost ~$0.25 per review; SOTA models like Claude Opus or GPT-5 can run $5–$10 on a long paper. The cost estimate shown before submission is a ballpark, not a ceiling. Leave headroom or the review can exhaust the key halfway and fail. Unused credits don't expire.",
  setupOrStep2Annotation: "credits page",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "Amount",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "Balance: $0.00",
  // setup page — OpenRouter step 3
  setupOrStep3Title: "Create an API key",
  setupOrStep3BodyPrefix: "Go to ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: ", click “Create Key”, and name it ",
  setupOrStep3BodySuffix: ".",
  setupOrStep3Provisioning:
    "Make sure it's a regular API key — not a provisioning/management key from the integrations section. Provisioning keys can create and list other keys but can't run inference, and coarse will fail with “User not found” if you paste one.",
  setupOrStep3CopyWarning: "Copy the key now — you won't see it again.",
  setupOrStep3Annotation: "keys page",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "Key name",
  setupOrStep3MockYourKey: "Your key",
  // setup page — OpenRouter step 4
  setupOrStep4Title: "Set a spending limit on the key",
  setupOrStep4BodyPrefix: "On the ",
  setupOrStep4BodyLink: "Keys page",
  setupOrStep4BodyMid1: ", click the ",
  setupOrStep4BodyMid2: " menu next to your new key, choose “Edit”, and set the credit limit to ",
  setupOrStep4BodyAtLeast: "at least $20",
  setupOrStep4BodySuffix:
    ". The key stops working once the limit is hit, so surprise charges are impossible. But set it too tight and a single expensive review can exhaust it mid-run.",
  setupOrStep4Annotation: "key menu",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "Credit limit for this key",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "Why this matters:",
  setupOrStep4WhyMid1: " coarse is open-source — you can ",
  setupOrStep4WhyLink: "read every line of code",
  setupOrStep4WhySuffix:
    ". Your key is sent directly to OpenRouter to run the review, then discarded — it is never stored. But you don't have to trust us: the per-key limit guarantees it can never spend more than you allow, even in the worst case.",
  setupOrStep4CostLabel: "A note on cost estimates:",
  setupOrStep4CostBody:
    " the estimate shown before submission is a heuristic with a ~15% buffer, not a hard ceiling. Actual cost on SOTA models with long papers can run up to ~2× the estimate once proof-verification and critique rewrites kick in. If the per-key cap sits right at the estimate, one tough review can drain it and fail mid-run. Always leave headroom.",
  // setup page — OpenRouter step 5
  setupOrStep5Title: "Paste into coarse",
  setupOrStep5Body: "Come back here, paste your key into the form, and upload your PDF.",
  setupOrStep5Annotation: "coarse form",
  setupOrStep5MockEmail: "Email",
  setupOrStep5MockKey: "OpenRouter key",
  setupOrStep5MockButton: "Review my paper",
  // setup page — shared footer CTA
  setupReadyCta: "Ready? Review your paper →",
  // setup page — subscription tab intro
  setupSubHeading: "Use your coding-agent subscription",
  setupSubIntro1:
    "For users already paying for Claude Code, Codex, or Gemini CLI. The review runs on your subscription and bills there. You pay OpenRouter only for PDF OCR and any triggered vision QA.",
  setupSubIntro2:
    "Runs locally on your machine using your own Claude Code, Codex, or Gemini CLI account. coarse.ink does not receive or store your provider login. Your provider's terms and usage limits still apply. coarse.ink is not affiliated with Anthropic, OpenAI, or Google.",
  // setup page — subscription step 1
  setupSubStep1Title: "Install a coding agent",
  setupSubStep1Body:
    "Pick whichever one you pay for. Gemini CLI has a free tier if you don't. Install it from the vendor's own page — their docs stay up to date.",
  setupSubStep1ClaudePrice: "Anthropic Pro or Max",
  setupSubStep1CodexPrice: "ChatGPT Plus, Pro, or Business",
  setupSubStep1GeminiPrice: "Free tier works for most papers",
  setupSubStep1InstallLabel: "Install instructions ↗",
  setupSubStep1Verify:
    "Run the test command to verify install + login. If it prints a response, you're set.",
  setupSubStep1CardLogin: "login: ",
  setupSubStep1CardTest: "test: ",
  // setup page — subscription step 2
  setupSubStep2Title: "Put an OpenRouter key on your machine (PDFs only)",
  setupSubStep2BodyPrefix:
    "This step only applies to PDF papers — non-PDF sources (.tex, .md, .docx, …) are extracted locally without OCR, so they need no OpenRouter key anywhere and you can skip straight to step 3. For PDFs, coarse needs OpenRouter for OCR and any triggered vision QA. Follow the ",
  setupSubStep2BodyTab: "OpenRouter key",
  setupSubStep2BodySuffix:
    " tab to create an account, add $1 of credit, and set a $2 per-key limit. The $20 buffer from the OpenRouter-only path isn't needed here because the review itself runs on your coding-agent subscription.",
  setupSubStep2KeyPrefix: "Then put the key on your own machine: run ",
  setupSubStep2KeyMid1: ", drop it in a ",
  setupSubStep2KeyMid2: ", or save it to ",
  setupSubStep2KeySuffix:
    ". Your CLI reads it locally when it runs the extraction; coarse.ink never sees it.",
  // setup page — subscription step 3
  setupSubStep3Title: "Upload your paper and pick a CLI",
  setupSubStep3BodyPrefix: "On the ",
  setupSubStep3BodyLink: "main page",
  setupSubStep3BodyMid: ", drop your paper (PDF, .tex, .md, .docx, …) onto the form, then click the ",
  setupSubStep3BodyButton: "Review with my subscription ▾",
  setupSubStep3BodySuffix:
    " dropdown and pick your CLI. coarse uploads the file, mints a handoff token, and shows the prompt you'll paste in the next step. You don't paste your OpenRouter key on the form here; the CLI reads it from your machine (step 2).",
  // setup page — subscription step 4
  setupSubStep4Title: "Paste the prompt into your CLI",
  setupSubStep4BodyPrefix: "coarse gives you one natural-language prompt. Copy it from the panel, paste it into your ",
  setupSubStep4BodyMid1: ", ",
  setupSubStep4BodyMid2: ", or ",
  setupSubStep4BodyMid3: " session, and hit send. The agent refreshes its skill bundle, runs the full coarse pipeline on its own subprocess calls, and prints a ",
  setupSubStep4BodySuffix:
    " URL when it's done. 10–25 minutes. Click the URL to open the finished review on coarse.ink.",
  setupSubStep4TimeoutLabel: "If you're pasting into a coding agent",
  setupSubStep4TimeoutSuffix:
    " (not a plain terminal), bump its bash-tool timeout to at least 45 min before you send the prompt. Default agent timeouts can be as low as 2 min, way under the 10–25 min review runtime.",
  // setup page — subscription step 5 (troubleshooting)
  setupSubStep5Title: "If something goes wrong",
  setupSubTrouble1Symptom: "The “Try opening Claude Code / Codex” button does nothing.",
  setupSubTrouble1Fix:
    "The button only works if you have the desktop app installed. With a CLI-only install, the browser can't launch a terminal for you. Copy the prompt from the panel and paste it into your CLI manually.",
  setupSubTrouble2Symptom: "“No such command ‘install-skills’” inside the agent run.",
  setupSubTrouble2FixPrefix: "Safe to ignore. The skill bundle still loads directly through ",
  setupSubTrouble2FixSuffix: "; the agent will continue to the review step.",
  setupSubTrouble3Symptom: "My Anthropic / OpenAI / Google bill went up after a review.",
  setupSubTrouble3FixPrefix: "Check for ",
  setupSubTrouble3FixMid1: ", ",
  setupSubTrouble3FixMid2: ", or ",
  setupSubTrouble3FixSuffix:
    " in your shell environment. If set, the host CLI bills the API account instead of your subscription. v1.3.0+ strips these automatically, but older versions didn't.",
  setupSubTrouble4Symptom: "Fewer comments than usual (~10 instead of 15–25).",
  setupSubTrouble4FixPrefix: "A section hit the 30-min timeout and got dropped. Rare on default effort, more common with ",
  setupSubTrouble4FixSuffix:
    " on long papers. Re-run; drop effort one notch if it happens twice.",

  // compare page (ComparePage.tsx)
  comparePanelErrorBody: "Couldn't render this one. Try another model or comparison.",
  comparePaperCorticalCircuits: "Cortical Circuits",
  comparePaperCosetCodes: "Coset Codes",
  comparePaperPopulationGenetics: "Population Genetics",
  comparePaperTargetingInterventions: "Targeting Interventions",
  compareScoresShow: "Show",
  compareScoresHide: "Hide",
  compareScoresToggleSuffix: " all scores across papers ",
  compareScoresColPaper: "Paper",
  compareScoresColReference: "Reference",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "Evaluated by Gemini 3.1 Pro with PDF multimodal input. 5.0/5 = matches reference quality. 5.5+/5 = exceeds it.",
  compareJudgeShow: "Show",
  compareJudgeHide: "Hide",
  compareJudgeToggleSuffix: " judge prompt sent to Gemini 3.1 Pro ",
  compareJudgeExplain:
    "To mitigate known LLM-as-judge biases, the judge is run twice per evaluation with the two reviews swapped in presentation order, and scores are averaged across both orderings. This counteracts positional bias, where judges systematically favor whichever review appears first. The prompt also includes specific instructions to counteract verbosity bias (not rewarding length over substance), confidence bias (not rewarding assertive language over correct hedging), authority bias (not rewarding jargon or citation count over accuracy), and leniency bias (using the full 1-6 scoring range rather than clustering in the middle). Reviews are labeled neutrally as \"Review A\" and \"Review B\" rather than \"reference\" and \"generated\" to prevent provenance-based scoring.",
  compareJudgeSystemPromptLabel: "System prompt",
  compareJudgeUserPromptLabel: "User prompt (paper + reviews injected at runtime)",
  compareVsMid: " vs ",
  compareScoreOutOf: "/5",
  compareMetricCoverage: "Coverage",
  compareMetricSpecificity: "Specificity",
  compareMetricDepth: "Depth",
  compareJumpTo: "Jump to",
  compareSectionOverallFeedback: "Overall Feedback",
  compareSectionDetailedComments: "Detailed Comments",
  compareVisitPrefix: "Visit ",
  comparePdfReviewSuffix: " review",
  comparePdfFallback: "Download PDF if iframe doesn't render ↓",
} as const;
