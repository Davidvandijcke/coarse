// Korean (ko) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const ko: Messages = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "사이트 언어",

  // copy-to-clipboard code block
  codeBlockCopied: "복사됨 ✓",
  codeBlockCopy: "복사",

  // header
  headerTagline: "동료 심사는 공공재입니다.",
  navSetup: "설정",
  navSideBySide: "나란히 비교",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "제출이 일시적으로 중단되었습니다.",
  bannerBusyPrefix: "시스템이 혼잡합니다 (",
  bannerBusySuffix: " 슬롯 사용 중). 리뷰가 대기열에 들어갈 수 있습니다.",
  bannerFasterPrefix: "더 빠른 결과를 원하시면 CLI를 사용해 보세요:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "안녕하세요 ",
  heroGreetingSuffix: " 이 논문을 리뷰해 주실 수 있나요?",
  heroHeading: "‘coarse!",
  heroLede:
    "AI 에이전트가 논문을 리뷰하고 심사 보고서를 작성합니다. API 비용은 직접 지불하시면 됩니다. 계정이 필요 없습니다.",
  heroManifesto:
    "학술 동료 심사는 무보수 학술 노동으로 굴러갑니다. 누군가는 그것으로 사업을 벌이기로 했습니다. 우리는 그게 마음에 들지 않았습니다.",

  // hero — score preview
  scoreVsOthers: "다른 AI 리뷰어 대비",
  statCostNum: "< $2*",
  statCostLabel: "리뷰당",
  statCostFootnote: "*보통은 그렇습니다 :)",
  statCommentsNum: "20+",
  statCommentsLabel: "상세 코멘트",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "오픈 소스",

  // hero — competitive comparison
  comparePrefix: "블라인드 평가 대상:",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "훨씬 적은 비용으로 범위, 구체성, 깊이에서 더 높은 점수를 받습니다.",
  compareLink: "나란히 비교 보기 →",

  // submit form — section heading + paper field
  formSubmitHeading: "논문 제출",
  fieldPaper: "논문",
  dropzoneAriaLabel: "논문 업로드 — 파일을 끌어다 놓거나 클릭하여 찾아보세요",
  dropzoneInputAriaLabel: "업로드할 파일 선택",
  dropzoneReplaceSuffix: " MB — 클릭하거나 끌어다 놓아 교체",
  dropzonePromptPrefix: "여기에 파일을 끌어다 놓거나, ",
  dropzoneBrowse: "찾아보기",
  dropzoneMaxSize: "최대 50 MB",

  // submit form — email field
  fieldEmail: "이메일 ",
  fieldEmailQualifier: "(웹 리뷰 전용)",
  emailPlaceholderUnavailable: "— 사용할 수 없음 —",
  emailPlaceholder: "you@university.edu",
  emailAriaLabel: "이메일 주소",
  emailHelperDisabled:
    "이메일 전송이 일시적으로 중단되었습니다. 제출하실 때 리뷰 키를 저장해 두시고 약 한 시간 후에 다시 확인해 주세요.",
  emailHelperPrefix:
    "완료되면 이메일로 알려드립니다. 보이지 않으면 스팸 폴더를 확인해 주세요.",

  // submit form — OpenRouter key field
  fieldKey: "OpenRouter 키",
  fieldKeyGetOne: "발급받기 →",
  keyOrPaste: "— 또는 키를 붙여넣으세요 —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter API 키",
  keyHelper:
    "OAuth 키는 이 탭에만 유지되며 탭을 닫으면 삭제됩니다. 저희 서버에는 절대 저장되지 않습니다.",

  // submit form — author notes
  fieldNotes: "리뷰어에게 전하는 메모",
  fieldNotesOptional: "(선택 사항)",
  notesPlaceholder:
    "예: §3의 식별 전략에 집중해 주세요 — 데이터 섹션은 아직 임시 자리표시자입니다.",
  notesAriaLabel: "리뷰어의 초점을 안내하는 선택적 메모",
  notesHelper: "리뷰어가 무엇에 집중할지 안내합니다. 평가 기준을 덮어쓰지는 않습니다.",

  // submit form — cost estimate
  costEstimating: "비용 추정 중...",
  costEstimatePrefix: "예상 API 비용: $",
  costUnavailable: "이 모델은 비용 추정을 제공할 수 없습니다",

  // submit form — Turnstile failure block
  turnstileFailedLine1Prefix:
    "사람 확인을 완료하지 못했습니다. 무언가가 차단하거나 지연시키고 있습니다: ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — 보통 브라우저의 엄격한 개인정보 보호 모드(예: Safari의 추적 방지나 Firefox ETP 엄격 모드), 콘텐츠/광고 차단기(Brave Shields, 일부 목록의 uBlock Origin), 또는 느리거나 필터링된 네트워크가 원인입니다.",
  turnstileFailedLine2Prefix: "먼저 페이지를 새로고침해 보세요. 그래도 계속되면 ",
  turnstileFailedLine2Mid: " 을(를) 허용하세요, 대상: ",
  turnstileFailedLine2Suffix:
    " (콘텐츠 차단기를 끄거나 개인정보 보호 설정을 완화하세요), 또는 다른 브라우저를 사용해 보세요. 미리보기 URL에서는 배포 환경이 해당 호스트 이름을 Cloudflare Turnstile 위젯 허용 목록에 추가해야 할 수도 있습니다.",
  turnstileFailedLine3Prefix: "또는 자신의 OpenRouter 키로 coarse를 로컬에서 실행하세요: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  // submit form — buttons + handoff picker
  submitButton: "내 논문 리뷰하기",
  submitButtonBusy: "제출 중...",
  submitOr: "또는",
  handoffButton: "내 구독으로 리뷰하기 ▾",
  handoffButtonBusy: "준비 중...",

  // submit form — handoff progress messages
  handoffUploading: "논문 업로드 중...",
  handoffPreparing: "핸드오프 준비 중...",

  // submit form — explanatory paragraphs
  explainReviewLabel: "내 논문 리뷰하기:",
  explainReviewBody:
    " OpenRouter가 처음부터 끝까지 모두 처리합니다. 파일은 처리 후 삭제됩니다. 리뷰 키는 90일간 유효합니다. 보통 $2 미만입니다.",
  explainSubscriptionLabel: "내 구독으로 리뷰하기:",
  explainSubscriptionPart1:
    "전체 coarse 파이프라인을 로컬에서 실행하는 셸 명령을 드립니다. LLM 추론에는 ",
  explainSubscriptionYour: "당신의",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", 또는",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "구독을 사용합니다.",
  explainSubscriptionPdf:
    "로컬 Mistral OCR 단계에 대해서만 ~$0.10를 지불합니다(자신의 OpenRouter 키 사용). PDF가 아닌 업로드(.tex, .md, .docx, …)는 OCR을 건너뛰므로 OpenRouter 키가 필요 없습니다.",
  explainSubscriptionNonPdf:
    "파일이 PDF가 아니므로 Mistral OCR 단계를 완전히 건너뜁니다 — 전체 실행이 구독으로 처리되며 OpenRouter 키가 필요 없습니다.",
  explainSubscriptionPart3: "리뷰는 완료되면 이 페이지에 표시됩니다.",
  explainDisclaimer:
    "자신의 Claude Code, Codex 또는 Gemini CLI 계정을 사용하여 사용자의 컴퓨터에서 로컬로 실행됩니다. coarse.ink는 사용자의 제공자 로그인을 수신하거나 저장하지 않으며, 제공자의 약관, 사용 한도 및 조직 정책이 적용됩니다. coarse.ink는 Anthropic, OpenAI 또는 Google과 제휴 관계가 없습니다.",

  // submit form — handoff result card
  handoffReviewWithPrefix: "리뷰에 사용할 도구: ",
  handoffModelLabel: "모델",
  handoffEffortLabel: "추론 강도",
  handoffPastePromptPrefix: "이 프롬프트를 다음의 ",
  handoffPastePromptSuffix: " 터미널에 붙여넣으세요:",
  handoffRunHint:
    "에이전트가 coarse-review 스킬을 새로 고친 뒤 전체 리뷰를 로컬에서 실행하며, 10–25분이 걸립니다. 제공자 로그인은 사용자의 컴퓨터에 그대로 유지됩니다.",
  handoffKeyNeededPrefix:
    "OpenRouter 키가 먼저 사용자의 컴퓨터에 있어야 합니다 — 다음을 내보내세요: ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: ", 또는 다음에 넣으세요: ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " 또는 ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    ". 핸드오프 URL이 에이전트의 채팅 로그에 남기 때문에 키를 브라우저를 통해 전달하지 않습니다. 키가 없으면 에이전트가 요청할 것입니다.",
  handoffKeyNotNeeded:
    "이 논문에는 OpenRouter 키가 필요 없습니다 — PDF가 아니므로 추출이 Mistral OCR 단계 없이 로컬에서 실행됩니다.",
  handoffReviewUrlIntro: "리뷰가 완료되면 다음 주소에 표시됩니다:",
  handoffInstallPrefix: "아직 ",
  handoffInstallSuffix: " 이(가) 없으신가요? ",
  handoffInstallLink: "설치하기 →",

  // retrieve
  findReviewHeading: "리뷰 찾기",
  findReviewPlaceholder: "리뷰 키, 전체 리뷰 링크 또는 이전 리뷰 ID를 붙여넣으세요...",
  findReviewAriaLabel: "리뷰 키",
  findReviewButton: "찾기",

  // footer
  footerPrivacy: "개인정보처리방침",
  footerTerms: "이용약관",
  footerContact: "문의",

  // status / errors (set in handlers)
  noticeKeyMigrated:
    "저장된 OpenRouter 키를 이 탭에서만 유지되는 저장소로 옮겼습니다. 이 탭을 닫으면 삭제됩니다.",
  errorLoginNoPersist:
    "로그인되었지만 키를 이 탭에 유지할 수 없었습니다. 이 페이지를 새로고침하면 키를 다시 붙여넣어야 합니다.",
  errorLoginFailed:
    "OpenRouter 로그인에 실패했습니다. 다시 시도하거나 키를 직접 붙여넣어 주세요.",
  errorAuthFailed:
    "인증에 실패했습니다. 미리보기 배포에서는 보통 브라우저에 캐시된 Basic Auth 자격 증명이 폼 제출 시 함께 전송되지 않은 경우입니다. 탭을 새로고침하고(Cmd/Ctrl+Shift+R) 비밀번호 프롬프트에서 다시 로그인한 후 재시도해 주세요.",
  errorServiceUnavailable: "서비스를 일시적으로 사용할 수 없습니다 — 잠시 후 다시 시도해 주세요.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "사람 확인 위젯을 불러오지 못했습니다 — 브라우저 확장 프로그램(Brave Shields, uBlock Origin, Firefox ETP 엄격 모드)이 challenges.cloudflare.com을 차단하고 있을 가능성이 높습니다. 다음에 대해 비활성화해 보세요: ",
  errorTurnstileBlockedSuffix: ", 또는 coarse를 로컬에서 실행하세요: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "아직 사람 확인이 로드되기를 기다리는 중입니다 — 잠시 기다린 후 다시 시도해 주세요.",
  errorPrepareUpload: "업로드 준비에 실패했습니다",
  errorUploadFailed: "파일 업로드에 실패했습니다 — 다시 시도해 주세요",
  errorSubmissionFailed: "제출에 실패했습니다",
  errorHandoffFailed: "핸드오프에 실패했습니다",
  launchCommandCopied: "명령이 클립보드에 복사되었습니다. 터미널에 붙여넣으세요.",
  launchOpeningCodex:
    "Codex 데스크톱 앱을 여는 중입니다 — 입력창이 미리 채워져 있을 것입니다. 전송을 누르세요.",
  launchOpeningPrefix: "여는 중: ",
  launchOpeningSuffix: " — 클립보드에서 프롬프트를 붙여넣으세요(⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " 데스크톱 앱이 열리지 않았습니다. CLI 버전만 설치하신 경우 위 명령을 대신 터미널에 붙여넣으세요.",
  errorLoginCouldNotStartPrefix: "OpenRouter 로그인을 시작할 수 없었습니다: ",

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "리뷰 언어",
  reviewLanguageAuto: "자동 — 논문의 언어에 맞춤",
  reviewLanguageHelper:
    "기본값은 논문 자체의 언어입니다. 인용문은 항상 원문 그대로 유지됩니다.",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "모델",
  modelPickerUnavailableTitle: "현재 사용할 수 없음",
  modelPickerSearchPlaceholder: "모델 검색...",
  modelPickerLoading: "모델 불러오는 중...",
  modelPickerNoResults: "모델을 찾을 수 없습니다.",
  modelPickerSearch: "모델 검색...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "OpenRouter에 연결됨",
  openRouterLogOut: "로그아웃",
  openRouterLogIn: "OpenRouter로 로그인 →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "이 리뷰를 보려면 전체 보안 리뷰 링크 또는 리뷰 키가 필요합니다.",
  statusLoadFailed: "리뷰 상태를 불러오지 못했습니다. 다시 시도해 주세요.",
  statusCancelledByUser: "사용자가 리뷰를 취소했습니다",
  statusLoading: "불러오는 중",
  statusAccessTokenRequired: "액세스 토큰이 필요합니다.",
  statusNotFoundHeading: "리뷰를 찾을 수 없습니다.",
  statusNotFoundBody: "리뷰 키를 확인하고 다시 시도해 주세요.",
  statusCancelConfirmHeading: "리뷰를 취소하시겠습니까?",
  statusCancelConfirmBody: "정말 취소하시겠습니까? 결과를 확인할 수 없게 됩니다.",
  statusCancelling: "취소하는 중...",
  statusYesCancel: "네, 취소합니다",
  statusGoBack: "돌아가기",
  statusLabelCancelled: "취소됨",
  statusLabelFailed: "실패",
  statusLabelReviewing: "리뷰 중",
  statusLabelQueued: "대기 중",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "논문을 읽는 중입니다.",
  statusQueuedHeading: "대기 중입니다.",
  statusRunningBody: "리뷰 파이프라인을 실행하는 중입니다(보통 30–60분).",
  statusQueuedBody: "리뷰가 대기열에 있으며 곧 시작됩니다.",
  statusEmailWhenDone: "완료되면 이메일로 알려드립니다.",
  statusCancelledHeading: "리뷰가 취소되었습니다.",
  statusCancelledBody:
    "대기 중이던 작업이 취소로 표시되었습니다. 이미 작업이 시작된 경우 워커가 마무리되는 데 약간의 시간이 걸릴 수 있습니다.",
  statusFailedHeading: "실패했습니다.",
  statusUnexpectedError: "예기치 않은 오류가 발생했습니다.",
  statusResubmitPrefix: "다시 제출해 보시거나, 다음에 문제를 알려 주세요: ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: ".",
  statusTryAgain: "다시 시도 →",
  statusKeyBoxSave: "리뷰 키 — 저장해 두세요",
  statusKeyBoxLegacy: "이전 리뷰 링크",
  statusCopied: "복사됨",
  statusCopyLink: "링크 복사",
  statusRedirectNote: "리뷰가 준비되면 이 페이지가 자동으로 이동합니다.",
  statusCancelReview: "리뷰 취소",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "이 리뷰를 보려면 전체 보안 리뷰 링크 또는 리뷰 키가 필요합니다.",
  reviewClientLoadFailed: "리뷰를 불러오지 못했습니다. 다시 시도해 주세요.",
  reviewClientLoading: "불러오는 중",
  reviewClientNotFoundHeading: "리뷰를 찾을 수 없습니다.",
  reviewClientNotFoundBody: "키를 확인하고 다시 시도해 주세요.",
  reviewClientSubmitNewPaper: "새 논문 제출 →",
  reviewClientAccessTokenRequired: "액세스 토큰이 필요합니다.",
  reviewClientBackHome: "홈으로 →",
  reviewClientReadingHeading: "논문을 읽는 중입니다.",
  reviewClientQueuedHeading: "대기 중입니다.",
  reviewClientRunningBody: "보통 30–60분이 걸립니다. 이 페이지는 자동으로 업데이트됩니다.",
  reviewClientQueuedBody: "곧 처리가 시작됩니다.",
  reviewClientFailedHeading: "리뷰에 실패했습니다.",
  reviewClientUnexpectedError: "예기치 않은 오류가 발생했습니다.",
  reviewClientTryAgain: "다시 시도 →",
  reviewClientCancelledHeading: "리뷰가 취소되었습니다.",
  reviewClientCancelledBody: "이 리뷰는 완료되기 전에 취소되었습니다.",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "간략히 보기",
  reviewShowMore: "더 보기",
  reviewShowInPaper: "논문에서 보기",
  reviewMarkActive: "활성으로 표시",
  reviewMarkDone: "완료로 표시",
  reviewDismiss: "무시",
  reviewDiscuss: "토론",
  reviewDiscussTitle: "이 코멘트를 AI 모델과 토론하기",
  reviewShowDetails: "세부 정보 보기",
  reviewStatusDone: "완료",
  reviewStatusDismissed: "무시됨",
  reviewHide: "숨기기",
  reviewFilterAll: "전체",
  reviewFilterActive: "활성",
  reviewFilterDone: "완료",
  reviewFilterDismissed: "무시됨",
  reviewSidebarOverallFeedback: "전체 피드백",
  reviewSidebarCommentsPrefix: "코멘트 (",
  reviewSidebarCommentsRemainingSuffix: " 남음)",
  reviewRemainingSuffix: " 남음",
  reviewDownload: "다운로드",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "인쇄 / PDF",
  reviewHidePaper: "논문 숨기기",
  reviewShowPaper: "논문 보기",
  reviewCopied: "복사됨",
  reviewShare: "공유",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "끌어서 논문 패널 크기 조절",
  reviewResizeTitle: "끌어서 크기 조절",
  reviewOfPrefix: "리뷰 대상: ",
  reviewMetaModel: "모델",
  reviewMetaDate: "날짜",
  reviewMetaDomain: "분야",
  reviewMetaTime: "소요 시간",
  reviewMetaCost: "비용",
  reviewMetaReviewLanguage: "리뷰 언어",
  reviewMetaAutoDetectedSuffix: " · 자동 감지됨",
  reviewOverallFeedbackHeading: "전체 피드백",
  reviewDetailedCommentsPrefix: "상세 코멘트 (",
  reviewDetailedCommentsSuffix: ")",
  reviewGeneratedByPrefix: "생성: ",
  reviewGeneratedBySuffix: ". 당연하죠.",
  reviewShareThisReview: "이 리뷰 공유하기",
  reviewDeleteReview: "리뷰 삭제",
  reviewDeleteConfirmHeading: "리뷰를 삭제하시겠습니까?",
  reviewDeleteConfirmBody: "정말 삭제하시겠습니까? 결과를 확인할 수 없게 됩니다.",
  reviewDeleting: "삭제하는 중...",
  reviewYesDelete: "네, 삭제합니다",
  reviewGoBack: "돌아가기",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "이 비판이 실제로 타당한가요?",
  chatExamplePrompt2: "이를 반영하려면 어떻게 수정해야 하나요?",
  chatExamplePrompt3: "논문의 어느 부분에 해당하나요?",
  chatNoResponse: "모델로부터 응답이 없습니다. 다시 시도하거나 모델을 바꿔 보세요.",
  chatSessionExpired: "OpenRouter 세션이 만료되었습니다. 계속하려면 다시 로그인하세요.",
  chatSomethingWrong: "문제가 발생했습니다.",
  chatDiscussKicker: "토론 · ",
  chatKickerComment: "코멘트 #",
  chatKickerOverallFeedback: "전체 피드백",
  chatDiscussAriaPrefix: "토론: ",
  chatCloseAriaLabel: "채팅 닫기",
  chatDisconnectKeyTitle:
    "OpenRouter 키 연결 해제(이 탭을 벗어나 저장되지 않습니다)",
  chatDisconnectKey: "키 연결 해제",
  chatInputPlaceholder: "이 코멘트에 대해 물어보세요…",
  chatMessageAriaLabel: "메시지",
  chatStop: "중지",
  chatSend: "전송",
  chatModelDisclosurePrefix: "모델: ",
  chatKeyGateIntro:
    "이 코멘트에 대해 대화하려면 OpenRouter를 연결하세요. 키는 OpenRouter로 곧바로 전송되며 — 저희 서버로는 전송되지 않고 — 이 탭을 닫으면 삭제됩니다.",
  chatKeyGateOrPaste: "— 또는 키를 붙여넣으세요 —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "OpenRouter API 키",
  chatKeyGateUseKey: "키 사용",
  chatKeyGateHelper:
    "OAuth 키는 이 탭에만 유지되며 탭을 닫으면 삭제됩니다. 저희 서버에는 절대 저장되지 않습니다.",
  chatEmptyHintPrefix: "이 코멘트에 대해 무엇이든 물어보세요. 각 메시지는 ",
  chatEmptyHintFullPaper: "논문 전문",
  chatEmptyHintQuotedPassage: "인용된 구절과 피드백",
  chatEmptyHintSuffix: " 을(를) 맥락으로 전송하며 사용자의 OpenRouter 크레딧으로 실행됩니다.",
  chatEmptyHintNoPaper:
    "이 리뷰에는 논문 전문이 저장되어 있지 않으므로, 답변은 인용된 구절과 피드백에만 의존합니다.",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "열었습니다: ",
  handoffMenuOpenedPromptMid: " — 프롬프트가 미리 채워져 있습니다. coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md를 첨부한 다음 전송하세요. (혹시 몰라 프롬프트도 복사해 두었습니다.)",
  handoffMenuOpenedPlainMid: " — coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md를 첨부하고 복사된 프롬프트를 붙여넣으세요.",
  handoffMenuButtonTitle:
    "논문 + 리뷰를 자신의 AI 채팅(Claude, ChatGPT, Gemini, Grok, DeepSeek)으로 보내기",
  handoffMenuButton: "내 AI와 토론하기",
  handoffMenuDownloadsIntro: "논문 + 리뷰를 다운로드한 뒤 다음을 엽니다:",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "논문",
  paperPanelDownload: "다운로드",
  paperPanelDownloadAriaLabel: "논문 마크다운 다운로드",
  paperPanelCloseAriaLabel: "논문 패널 닫기",

  // setup page (setup/page.tsx)
  // setup page — tab switcher
  setupTablistAriaLabel: "설정 경로",
  setupTabOpenRouter: "OpenRouter 키",
  setupTabSubscription: "내 구독 사용하기",
  // setup page — OpenRouter tab intro
  setupOrHeading: "OpenRouter 키 발급받기",
  setupOrIntro:
    "약 2분이 걸립니다. 시작하려면 ~$1의 크레딧을 위한 신용카드가 필요합니다 — 2단계에서 $20까지 충전하시게 됩니다.",
  setupOrFasterLabel: "더 빠른 방법:",
  setupOrFasterMid1: " 메인 폼에서 ",
  setupOrFasterLogIn: "“OpenRouter로 로그인”",
  setupOrFasterSuffix:
    " 을(를) 클릭하면 coarse를 승인하고 수동 키 생성을 건너뛸 수 있습니다. 여전히 크레딧이 있는 OpenRouter 계정이 필요하며(아래 1단계와 2단계), 키별 지출 한도 설정(4단계)도 권장합니다.",
  // setup page — OpenRouter step 1
  setupOrStep1Title: "계정 만들기",
  setupOrStep1BodyPrefix: "다음으로 이동하세요: ",
  setupOrStep1BodySuffix: " 그런 다음 “Get API Key”를 클릭하거나 Google / GitHub으로 가입하세요.",
  setupOrStep1Annotation: "홈페이지",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "LLM을 위한 통합 API — 하나의 키로 여러 모델을.",
  // setup page — OpenRouter step 2
  setupOrStep2Title: "크레딧 추가",
  setupOrStep2BodyPrefix: "다음으로 이동하세요: ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    ". 최소 $20를 추가하세요. 저렴한 오픈 소스 모델은 리뷰당 ~$0.25, Claude Opus나 GPT-5 같은 SOTA 모델은 긴 논문에서 $5–$10가 들 수 있습니다. 제출 전에 표시되는 비용 추정치는 대략적인 값일 뿐 상한선이 아닙니다. 여유를 두지 않으면 리뷰가 중간에 키를 소진하고 실패할 수 있습니다. 사용하지 않은 크레딧은 만료되지 않습니다.",
  setupOrStep2Annotation: "크레딧 페이지",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "금액",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "Balance: $0.00",
  // setup page — OpenRouter step 3
  setupOrStep3Title: "API 키 만들기",
  setupOrStep3BodyPrefix: "다음으로 이동하세요: ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: ", “Create Key”를 클릭하고 이름을 다음으로 지정하세요: ",
  setupOrStep3BodySuffix: ".",
  setupOrStep3Provisioning:
    "반드시 일반 API 키여야 합니다 — integrations 섹션의 프로비저닝/관리 키가 아니어야 합니다. 프로비저닝 키는 다른 키를 생성하고 나열할 수 있지만 추론은 실행할 수 없으며, 이런 키를 붙여넣으면 coarse가 “User not found” 오류로 실패합니다.",
  setupOrStep3CopyWarning: "지금 키를 복사하세요 — 다시 볼 수 없습니다.",
  setupOrStep3Annotation: "키 페이지",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "키 이름",
  setupOrStep3MockYourKey: "당신의 키",
  // setup page — OpenRouter step 4
  setupOrStep4Title: "키에 지출 한도 설정하기",
  setupOrStep4BodyPrefix: "다음에서: ",
  setupOrStep4BodyLink: "키 페이지",
  setupOrStep4BodyMid1: ", 새 키 옆의 ",
  setupOrStep4BodyMid2: " 메뉴를 클릭하고 “Edit”를 선택한 다음 크레딧 한도를 다음으로 설정하세요: ",
  setupOrStep4BodyAtLeast: "최소 $20",
  setupOrStep4BodySuffix:
    ". 한도에 도달하면 키가 작동을 멈추므로 예상치 못한 청구는 불가능합니다. 하지만 너무 빡빡하게 설정하면 비싼 리뷰 하나가 실행 도중에 키를 소진시킬 수 있습니다.",
  setupOrStep4Annotation: "키 메뉴",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "이 키의 크레딧 한도",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "이것이 중요한 이유:",
  setupOrStep4WhyMid1: " coarse는 오픈 소스입니다 — 다음을 할 수 있습니다: ",
  setupOrStep4WhyLink: "모든 코드 줄 읽어보기",
  setupOrStep4WhySuffix:
    ". 키는 리뷰를 실행하기 위해 OpenRouter로 직접 전송된 뒤 폐기되며 — 절대 저장되지 않습니다. 하지만 저희를 믿으실 필요는 없습니다: 키별 한도가 최악의 경우에도 허용한 금액 이상을 절대 쓸 수 없도록 보장합니다.",
  setupOrStep4CostLabel: "비용 추정치에 관한 참고 사항:",
  setupOrStep4CostBody:
    " 제출 전에 표시되는 추정치는 ~15% 여유를 둔 휴리스틱이며 엄격한 상한선이 아닙니다. 긴 논문에 SOTA 모델을 사용하면 증명 검증과 비판 재작성이 작동하기 시작하면서 실제 비용이 추정치의 ~2배까지 들 수 있습니다. 키별 상한이 추정치에 딱 맞춰져 있으면 까다로운 리뷰 하나가 이를 소진하고 실행 도중에 실패할 수 있습니다. 항상 여유를 두세요.",
  // setup page — OpenRouter step 5
  setupOrStep5Title: "coarse에 붙여넣기",
  setupOrStep5Body: "여기로 돌아와 키를 폼에 붙여넣고 PDF를 업로드하세요.",
  setupOrStep5Annotation: "coarse 폼",
  setupOrStep5MockEmail: "이메일",
  setupOrStep5MockKey: "OpenRouter 키",
  setupOrStep5MockButton: "내 논문 리뷰하기",
  // setup page — shared footer CTA
  setupReadyCta: "준비되셨나요? 논문을 리뷰하세요 →",
  // setup page — subscription tab intro
  setupSubHeading: "코딩 에이전트 구독 사용하기",
  setupSubIntro1:
    "이미 Claude Code, Codex 또는 Gemini CLI에 비용을 지불하고 있는 사용자를 위한 방법입니다. 리뷰는 사용자의 구독으로 실행되어 거기에 청구됩니다. OCR 단계에 대해서만 OpenRouter에 ~$0.15를 지불합니다.",
  setupSubIntro2:
    "자신의 Claude Code, Codex 또는 Gemini CLI 계정을 사용하여 사용자의 컴퓨터에서 로컬로 실행됩니다. coarse.ink는 사용자의 제공자 로그인을 수신하거나 저장하지 않습니다. 제공자의 약관과 사용 한도는 여전히 적용됩니다. coarse.ink는 Anthropic, OpenAI 또는 Google과 제휴 관계가 없습니다.",
  // setup page — subscription step 1
  setupSubStep1Title: "코딩 에이전트 설치하기",
  setupSubStep1Body:
    "비용을 지불하고 있는 것 중 아무거나 고르세요. 없다면 Gemini CLI에 무료 등급이 있습니다. 벤더의 자체 페이지에서 설치하세요 — 해당 문서가 최신 상태로 유지됩니다.",
  setupSubStep1ClaudePrice: "Anthropic Pro 또는 Max",
  setupSubStep1CodexPrice: "ChatGPT Plus, Pro 또는 Business",
  setupSubStep1GeminiPrice: "대부분의 논문에는 무료 등급으로 충분합니다",
  setupSubStep1InstallLabel: "설치 안내 ↗",
  setupSubStep1Verify:
    "테스트 명령을 실행하여 설치 + 로그인을 확인하세요. 응답이 출력되면 준비된 것입니다.",
  setupSubStep1CardLogin: "로그인: ",
  setupSubStep1CardTest: "테스트: ",
  // setup page — subscription step 2
  setupSubStep2Title: "사용자 컴퓨터에 OpenRouter 키 두기 (PDF만 해당)",
  setupSubStep2BodyPrefix:
    "이 단계는 PDF 논문에만 적용됩니다 — PDF가 아닌 소스(.tex, .md, .docx, …)는 OCR 없이 로컬에서 추출되므로 어디에도 OpenRouter 키가 필요 없으며 바로 3단계로 건너뛸 수 있습니다. PDF의 경우 coarse는 OCR 단계(논문당 ~$0.10)에 여전히 OpenRouter가 필요합니다. 다음 ",
  setupSubStep2BodyTab: "OpenRouter 키",
  setupSubStep2BodySuffix:
    " 탭을 따라 계정을 만들고, $1의 크레딧을 추가하고, $2의 키별 한도를 설정하세요. OpenRouter 전용 경로의 $20 여유분은 여기서는 필요하지 않습니다. 리뷰 자체가 코딩 에이전트 구독으로 실행되기 때문입니다.",
  setupSubStep2KeyPrefix: "그런 다음 키를 자신의 컴퓨터에 두세요: 다음을 실행하거나 ",
  setupSubStep2KeyMid1: ", 다음에 넣거나 ",
  setupSubStep2KeyMid2: ", 다음에 저장하세요 ",
  setupSubStep2KeySuffix:
    ". CLI가 추출을 실행할 때 로컬에서 키를 읽습니다. coarse.ink는 키를 절대 보지 않습니다.",
  // setup page — subscription step 3
  setupSubStep3Title: "논문 업로드하고 CLI 선택하기",
  setupSubStep3BodyPrefix: "다음에서: ",
  setupSubStep3BodyLink: "메인 페이지",
  setupSubStep3BodyMid: ", 논문(PDF, .tex, .md, .docx, …)을 폼에 끌어다 놓은 다음 ",
  setupSubStep3BodyButton: "내 구독으로 리뷰하기 ▾",
  setupSubStep3BodySuffix:
    " 드롭다운을 클릭하고 CLI를 선택하세요. coarse가 파일을 업로드하고 핸드오프 토큰을 발급한 뒤 다음 단계에서 붙여넣을 프롬프트를 보여줍니다. 여기 폼에는 OpenRouter 키를 붙여넣지 않습니다. CLI가 사용자의 컴퓨터에서 키를 읽습니다(2단계).",
  // setup page — subscription step 4
  setupSubStep4Title: "프롬프트를 CLI에 붙여넣기",
  setupSubStep4BodyPrefix: "coarse가 하나의 자연어 프롬프트를 제공합니다. 패널에서 복사하여 다음 ",
  setupSubStep4BodyMid1: ", ",
  setupSubStep4BodyMid2: ", 또는 ",
  setupSubStep4BodyMid3: " 세션에 붙여넣고 전송을 누르세요. 에이전트가 스킬 번들을 새로 고치고, 자체 하위 프로세스 호출로 전체 coarse 파이프라인을 실행한 뒤 완료되면 ",
  setupSubStep4BodySuffix:
    " URL을 출력합니다. 10–25분이 걸립니다. URL을 클릭하면 완성된 리뷰가 coarse.ink에서 열립니다.",
  setupSubStep4TimeoutLabel: "코딩 에이전트에 붙여넣는 경우",
  setupSubStep4TimeoutSuffix:
    " (일반 터미널이 아닌 경우) 프롬프트를 전송하기 전에 bash 도구 타임아웃을 최소 45분으로 늘리세요. 기본 에이전트 타임아웃은 2분 정도로 낮을 수 있어 10–25분의 리뷰 실행 시간에 훨씬 못 미칩니다.",
  // setup page — subscription step 5 (troubleshooting)
  setupSubStep5Title: "문제가 발생하면",
  setupSubTrouble1Symptom: "“Try opening Claude Code / Codex” 버튼을 눌러도 아무 일이 일어나지 않습니다.",
  setupSubTrouble1Fix:
    "이 버튼은 데스크톱 앱이 설치되어 있어야만 작동합니다. CLI만 설치된 경우 브라우저가 터미널을 대신 실행할 수 없습니다. 패널에서 프롬프트를 복사하여 CLI에 직접 붙여넣으세요.",
  setupSubTrouble2Symptom: "에이전트 실행 중 “No such command ‘install-skills’”.",
  setupSubTrouble2FixPrefix: "무시해도 안전합니다. 스킬 번들은 여전히 다음을 통해 직접 로드됩니다: ",
  setupSubTrouble2FixSuffix: "; 에이전트는 리뷰 단계로 계속 진행합니다.",
  setupSubTrouble3Symptom: "리뷰 후 Anthropic / OpenAI / Google 청구액이 늘었습니다.",
  setupSubTrouble3FixPrefix: "다음을 확인하세요: ",
  setupSubTrouble3FixMid1: ", ",
  setupSubTrouble3FixMid2: ", 또는 ",
  setupSubTrouble3FixSuffix:
    " 가 셸 환경에 있는지 확인하세요. 설정되어 있으면 호스트 CLI가 구독 대신 API 계정에 청구합니다. v1.3.0+에서는 이를 자동으로 제거하지만 이전 버전에서는 그렇지 않았습니다.",
  setupSubTrouble4Symptom: "평소보다 코멘트가 적습니다(15–25개 대신 ~10개).",
  setupSubTrouble4FixPrefix: "한 섹션이 30분 타임아웃에 걸려 누락되었습니다. 기본 추론 강도에서는 드물지만 긴 논문에 ",
  setupSubTrouble4FixSuffix:
    " 을(를) 사용하면 더 흔합니다. 다시 실행하세요. 두 번 발생하면 추론 강도를 한 단계 낮추세요.",

  // compare page (ComparePage.tsx)
  comparePanelErrorBody: "이것을 렌더링할 수 없었습니다. 다른 모델이나 비교를 시도해 보세요.",
  comparePaperCorticalCircuits: "Cortical Circuits",
  comparePaperCosetCodes: "Coset Codes",
  comparePaperPopulationGenetics: "Population Genetics",
  comparePaperTargetingInterventions: "Targeting Interventions",
  compareScoresShow: "보기",
  compareScoresHide: "숨기기",
  compareScoresToggleSuffix: " 논문별 전체 점수 ",
  compareScoresColPaper: "논문",
  compareScoresColReference: "참조",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "PDF 멀티모달 입력으로 Gemini 3.1 Pro가 평가했습니다. 5.0/5 = 참조 품질과 동등. 5.5+/5 = 그 이상.",
  compareJudgeShow: "보기",
  compareJudgeHide: "숨기기",
  compareJudgeToggleSuffix: " Gemini 3.1 Pro에 전송된 심사 프롬프트 ",
  compareJudgeExplain:
    "알려진 LLM-as-judge 편향을 완화하기 위해, 심사자는 평가마다 두 리뷰의 제시 순서를 바꿔 두 번 실행되며 점수는 두 순서에 걸쳐 평균을 냅니다. 이는 심사자가 먼저 나오는 리뷰를 체계적으로 선호하는 위치 편향에 대응합니다. 프롬프트에는 또한 장황함 편향(분량을 내용보다 우대하지 않음), 확신 편향(올바른 신중함보다 단정적인 표현을 우대하지 않음), 권위 편향(정확성보다 전문 용어나 인용 수를 우대하지 않음), 관대함 편향(중간에 몰리지 않고 1-6점 척도 전체를 사용)에 대응하기 위한 구체적인 지침이 포함됩니다. 리뷰는 출처 기반 채점을 방지하기 위해 \"참조\"와 \"생성됨\" 대신 \"Review A\"와 \"Review B\"로 중립적으로 표시됩니다.",
  compareJudgeSystemPromptLabel: "시스템 프롬프트",
  compareJudgeUserPromptLabel: "사용자 프롬프트(논문 + 리뷰가 런타임에 삽입됨)",
  compareVsMid: " vs ",
  compareScoreOutOf: "/5",
  compareMetricCoverage: "범위",
  compareMetricSpecificity: "구체성",
  compareMetricDepth: "깊이",
  compareJumpTo: "이동",
  compareSectionOverallFeedback: "전체 피드백",
  compareSectionDetailedComments: "상세 코멘트",
  compareVisitPrefix: "방문: ",
  comparePdfReviewSuffix: " 리뷰",
  comparePdfFallback: "iframe이 렌더링되지 않으면 PDF를 다운로드하세요 ↓",
};
