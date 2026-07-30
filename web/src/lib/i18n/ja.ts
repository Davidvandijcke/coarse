// Japanese (ja) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const ja: Messages = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "サイトの言語",

  // copy-to-clipboard code block
  codeBlockCopied: "コピーしました ✓",
  codeBlockCopy: "コピー",

  // header
  headerTagline: "査読は公共財です。",
  navSetup: "セットアップ",
  navSideBySide: "比較",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "投稿は一時的に停止しています。",
  bannerBusyPrefix: "システムが混雑しています（",
  bannerBusySuffix: " 件のスロットが使用中です）。レビューは順番待ちになる場合があります。",
  bannerFasterPrefix: "より速く結果を得るには、CLI をお試しください:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "ねえ ",
  heroGreetingSuffix: " この論文をレビューしてもらえる？",
  heroHeading: "‘coarse!",
  heroLede:
    "AI エージェントがあなたの論文をレビューし、査読レポートを作成します。API の費用はあなたが直接お支払いいただきます。アカウントは不要です。",
  heroManifesto:
    "学術的な査読は、無償の学術労働によって成り立っています。他社はそれをビジネスにすることにしました。私たちはそれが気に入りませんでした。",

  // hero — score preview
  scoreVsOthers: "他の AI レビュアーとの比較",
  statCostNum: "< $2*",
  statCostLabel: "1 回のレビューあたり",
  statCostFootnote: "*通常は :)",
  statCommentsNum: "20+",
  statCommentsLabel: "詳細なコメント",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "オープンソース",

  // hero — competitive comparison
  comparePrefix: "ブラインド評価で比較した相手:",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "カバレッジ、具体性、深さでより高いスコアを獲得 -- しかもごくわずかな費用で。",
  compareLink: "比較を見る →",

  // submit form — section heading + paper field
  formSubmitHeading: "論文を投稿する",
  fieldPaper: "論文",
  dropzoneAriaLabel: "論文をアップロード — ファイルをドロップするか、クリックして選択してください",
  dropzoneInputAriaLabel: "アップロードするファイルを選択",
  dropzoneReplaceSuffix: " MB — クリックまたはドロップで置き換え",
  dropzonePromptPrefix: "ここにファイルをドロップ、または ",
  dropzoneBrowse: "参照",
  dropzoneMaxSize: "最大 50 MB",

  // submit form — email field
  fieldEmail: "メール ",
  fieldEmailQualifier: "（ウェブレビューのみ）",
  emailPlaceholderUnavailable: "— 利用できません —",
  emailPlaceholder: "you@university.edu",
  emailAriaLabel: "メールアドレス",
  emailHelperDisabled:
    "メール配信は一時的に停止しています。投稿時にレビューキーを保存し、1 時間ほど経ってからもう一度ご確認ください。",
  emailHelperPrefix:
    "完了したらメールでお知らせします。届かない場合は迷惑メールフォルダーをご確認ください。",

  // submit form — OpenRouter key field
  fieldKey: "OpenRouter キー",
  fieldKeyGetOne: "取得する →",
  keyOrPaste: "— またはキーを貼り付け —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter API キー",
  keyHelper:
    "OAuth キーはこのタブ内にのみ保持され、タブを閉じると消去されます。当社のサーバーには一切保存されません。",

  // submit form — author notes
  fieldNotes: "レビュアーへのメモ",
  fieldNotesOptional: "（任意）",
  notesPlaceholder:
    "例: §3 の識別戦略に注目してください — データのセクションはまだ仮置きの状態です。",
  notesAriaLabel: "レビュアーの注目点を誘導する任意のメモ",
  notesHelper: "レビュアーが注目する点を誘導します。ルーブリックを上書きするものではありません。",
  deepLiteratureLabel: "詳細な文献検索",
  deepLiteratureHelper:
    "Perplexity Sonar Deep Research を使って、より網羅的な複数段階の情報源検索を行います。通常は数分長くかかり、見積もりに約 0.30 ドル追加されます。",
  deepLiteratureOn: "オン",
  deepLiteratureOff: "オフ",

  // submit form — cost estimate
  costEstimating: "費用を見積もっています...",
  costEstimatePrefix: "推定 API 費用: $",
  costUnavailable: "このモデルでは費用の見積もりを利用できません",

  // submit form — Turnstile failure block
  turnstileFailedLine1Prefix:
    "人間確認を完了できませんでした。何かが次の読み込みをブロックまたは遅延させています: ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — 多くの場合、ブラウザの厳格なプライバシーモード（Safari のトラッキング防止や Firefox ETP の厳格設定など）、コンテンツ/広告ブロッカー（Brave Shields、一部のリストでの uBlock Origin）、または低速もしくはフィルタリングされたネットワークが原因です。",
  turnstileFailedLine2Prefix: "まずページの再読み込みをお試しください。それでも解決しない場合は、 ",
  turnstileFailedLine2Mid: " に対して ",
  turnstileFailedLine2Suffix:
    " を許可してください（コンテンツブロッカーを無効にするか、プライバシー設定を緩めてください）。または別のブラウザをお使いください。プレビュー URL の場合は、デプロイ側で Cloudflare Turnstile ウィジェットの許可リストにそのホスト名を追加する必要があることもあります。",
  turnstileFailedLine3Prefix: "または、ご自身の OpenRouter キーで coarse をローカルで実行してください: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: "。",

  // submit form — buttons + handoff picker
  submitButton: "論文をレビューする",
  submitButtonBusy: "送信中...",
  submitOr: "または",
  handoffButton: "自分のサブスクリプションでレビュー ▾",
  handoffButtonBusy: "準備中...",

  // submit form — handoff progress messages
  handoffUploading: "論文をアップロード中...",
  handoffPreparing: "引き継ぎを準備中...",

  // submit form — explanatory paragraphs
  explainReviewLabel: "論文をレビューする:",
  explainReviewBody:
    " OpenRouter がすべてを最初から最後まで処理します。ファイルは処理後に削除されます。レビューキーは 90 日間有効です。通常は $2 未満です。",
  explainSubscriptionLabel: "自分のサブスクリプションでレビュー:",
  explainSubscriptionPart1:
    "coarse の完全なパイプラインをローカルで実行するシェルコマンドをお渡しします。LLM の推論には ",
  explainSubscriptionYour: "ご自身の",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: "、",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: "、または",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "のサブスクリプションを使用します。",
  explainSubscriptionPdf:
    "ローカルの Mistral OCR ステップ（ご自身の OpenRouter キーを使用）に対して ~$0.10 をお支払いいただくだけです。PDF 以外のアップロード（.tex, .md, .docx, …）は OCR をスキップするため、OpenRouter キーは不要です。",
  explainSubscriptionNonPdf:
    "ファイルが PDF ではないため、Mistral OCR ステップは完全にスキップされます — 実行全体がサブスクリプションでカバーされ、OpenRouter キーは不要です。",
  explainSubscriptionPart3: "レビューは完了するとこのページに表示されます。",
  explainDisclaimer:
    "ご自身の Claude Code、Codex、または Gemini CLI アカウントを使用して、ご自身のマシン上でローカルに実行されます。coarse.ink はあなたのプロバイダーのログイン情報を受信または保存することはなく、お使いのプロバイダーの利用規約、利用上限、組織のポリシーが適用されます。coarse.ink は Anthropic、OpenAI、Google とは提携していません。",

  // submit form — handoff result card
  handoffReviewWithPrefix: "レビューに使用: ",
  handoffModelLabel: "モデル",
  handoffEffortLabel: "推論の強度",
  handoffPastePromptPrefix: "このプロンプトを次の ",
  handoffPastePromptSuffix: " のターミナルに貼り付けてください:",
  handoffRunHint:
    "エージェントが coarse-review スキルを更新し、完全なレビューをローカルで実行します。所要時間は 10–25 分です。プロバイダーのログイン情報はあなたのマシン上に留まります。",
  handoffKeyNeededPrefix:
    "まず OpenRouter キーをあなたのマシンに用意する必要があります — 次をエクスポートするか ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: "、または次に設定してください ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " か ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    "。引き継ぎ URL はエージェントのチャットログに残るため、ブラウザ経由では送信しません。キーがない場合は、エージェントが尋ねます。",
  handoffKeyNotNeeded:
    "この論文には OpenRouter キーは不要です — PDF ではないため、抽出は Mistral OCR ステップなしでローカルに実行されます。",
  handoffReviewUrlIntro: "レビューが完了すると、次の場所に表示されます:",
  handoffInstallPrefix: "まだ ",
  handoffInstallSuffix: " をお持ちでないですか？ ",
  handoffInstallLink: "インストールする →",

  // retrieve
  findReviewHeading: "レビューを探す",
  findReviewPlaceholder: "レビューキー、完全なレビューリンク、または以前のレビュー ID を貼り付けてください...",
  findReviewAriaLabel: "レビューキー",
  findReviewButton: "検索",

  // footer
  footerPrivacy: "プライバシー",
  footerTerms: "利用規約",
  footerContact: "お問い合わせ",

  // status / errors (set in handlers)
  noticeKeyMigrated:
    "保存された OpenRouter キーをこのタブ専用のストレージに移動しました。このタブを閉じると消去されます。",
  errorLoginNoPersist:
    "ログインしましたが、キーをこのタブに保持できませんでした。このページが再読み込みされた場合は、もう一度貼り付ける必要があります。",
  errorLoginFailed:
    "OpenRouter のログインに失敗しました。もう一度お試しいただくか、手動でキーを貼り付けてください。",
  errorAuthFailed:
    "認証に失敗しました。プレビューデプロイでは、これは通常、ブラウザにキャッシュされた Basic 認証の資格情報がフォーム送信時に送られなかったことを意味します。タブを更新し（Cmd/Ctrl+Shift+R）、パスワードプロンプトで再度サインインしてから、もう一度お試しください。",
  errorServiceUnavailable: "サービスは一時的に利用できません — 1 分後にもう一度お試しください。",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "人間確認ウィジェットを読み込めませんでした — ブラウザ拡張機能（Brave Shields、uBlock Origin、Firefox ETP の厳格設定）が challenges.cloudflare.com をブロックしている可能性が高いです。次に対してそれを無効にしてみてください ",
  errorTurnstileBlockedSuffix: "。または coarse をローカルで実行してください: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "人間確認の読み込みをまだ待っています — 少し時間をおいてからもう一度お試しください。",
  errorPrepareUpload: "アップロードの準備に失敗しました",
  errorUploadFailed: "ファイルのアップロードに失敗しました — もう一度お試しください",
  errorSubmissionFailed: "送信に失敗しました",
  errorHandoffFailed: "引き継ぎに失敗しました",
  launchCommandCopied: "コマンドをクリップボードにコピーしました。ターミナルに貼り付けてください。",
  launchOpeningCodex:
    "Codex デスクトップアプリを開いています — コンポーザーに自動入力されるはずです。送信を押してください。",
  launchOpeningPrefix: "開いています: ",
  launchOpeningSuffix: " — クリップボードからプロンプトを貼り付けてください（⌘V / Ctrl+V）。",
  launchDidntOpenSuffix:
    " デスクトップアプリが開きませんでした。CLI 版のみをインストールしている場合は、代わりに上記のコマンドをターミナルに貼り付けてください。",
  errorLoginCouldNotStartPrefix: "OpenRouter のログインを開始できませんでした: ",

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "レビューの言語",
  reviewLanguageAuto: "自動 — 論文の言語に合わせる",
  reviewLanguageHelper:
    "デフォルトでは論文自体の言語を使用します。引用は常に原文のままです。",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "モデル",
  modelPickerUnavailableTitle: "現在利用できません",
  modelPickerSearchPlaceholder: "モデルを検索...",
  modelPickerLoading: "モデルを読み込み中...",
  modelPickerNoResults: "モデルが見つかりません。",
  modelPickerSearch: "モデルを検索...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "OpenRouter に接続済み",
  openRouterLogOut: "ログアウト",
  openRouterLogIn: "OpenRouter でログイン →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "このレビューには、完全な安全なレビューリンクまたはレビューキーが必要です。",
  statusLoadFailed: "レビューの状態を読み込めませんでした。もう一度お試しください。",
  statusCancelledByUser: "ユーザーによってレビューがキャンセルされました",
  statusLoading: "読み込み中",
  statusAccessTokenRequired: "アクセストークンが必要です。",
  statusNotFoundHeading: "レビューが見つかりません。",
  statusNotFoundBody: "レビューキーを確認して、もう一度お試しください。",
  statusCancelConfirmHeading: "レビューをキャンセルしますか？",
  statusCancelConfirmBody: "本当によろしいですか？結果を確認できなくなります。",
  statusCancelling: "キャンセル中...",
  statusYesCancel: "はい、キャンセルします",
  statusGoBack: "戻る",
  statusLabelCancelled: "キャンセル済み",
  statusLabelFailed: "失敗",
  statusLabelReviewing: "レビュー中",
  statusLabelQueued: "順番待ち",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "論文を読み込んでいます。",
  statusQueuedHeading: "順番待ちです。",
  statusRunningBody: "レビューのパイプラインを実行中です（通常 30–60 分）。",
  statusQueuedBody: "レビューは順番待ちに入っており、まもなく開始します。",
  statusEmailWhenDone: "完了したらメールでお知らせします。",
  statusCancelledHeading: "レビューをキャンセルしました。",
  statusCancelledBody:
    "順番待ちのジョブをキャンセル済みとして処理しました。すでに作業が始まっていた場合は、ワーカーが停止するまで少し時間がかかることがあります。",
  statusFailedHeading: "失敗しました。",
  statusUnexpectedError: "予期しないエラーが発生しました。",
  statusResubmitPrefix: "もう一度投稿し直すか、問題を次の場所に報告してください: ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: "。",
  statusTryAgain: "もう一度お試しください →",
  statusKeyBoxSave: "あなたのレビューキー — 保存してください",
  statusKeyBoxLegacy: "以前のレビューリンク",
  statusCopied: "コピーしました",
  statusCopyLink: "リンクをコピー",
  statusRedirectNote: "レビューの準備が整うと、このページは自動的にリダイレクトされます。",
  statusCancelReview: "レビューをキャンセル",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "このレビューには、完全な安全なレビューリンクまたはレビューキーが必要です。",
  reviewClientLoadFailed: "レビューを読み込めませんでした。もう一度お試しください。",
  reviewClientLoading: "読み込み中",
  reviewClientNotFoundHeading: "レビューが見つかりません。",
  reviewClientNotFoundBody: "キーを確認して、もう一度お試しください。",
  reviewClientSubmitNewPaper: "新しい論文を投稿する →",
  reviewClientAccessTokenRequired: "アクセストークンが必要です。",
  reviewClientBackHome: "ホームに戻る →",
  reviewClientReadingHeading: "論文を読み込んでいます。",
  reviewClientQueuedHeading: "順番待ちです。",
  reviewClientRunningBody: "通常 30–60 分かかります。このページは自動的に更新されます。",
  reviewClientQueuedBody: "まもなく処理を開始します。",
  reviewClientFailedHeading: "レビューに失敗しました。",
  reviewClientUnexpectedError: "予期しないエラーが発生しました。",
  reviewClientTryAgain: "もう一度お試しください →",
  reviewClientCancelledHeading: "レビューをキャンセルしました。",
  reviewClientCancelledBody: "このレビューは完了前にキャンセルされました。",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "簡易表示",
  reviewShowMore: "もっと見る",
  reviewShowInPaper: "論文内で表示",
  reviewMarkActive: "アクティブにする",
  reviewMarkDone: "完了にする",
  reviewDismiss: "却下",
  reviewDiscuss: "相談する",
  reviewDiscussTitle: "このコメントについて AI モデルと相談する",
  reviewShowDetails: "詳細を表示",
  reviewStatusDone: "完了",
  reviewStatusDismissed: "却下済み",
  reviewHide: "非表示",
  reviewFilterAll: "すべて",
  reviewFilterActive: "アクティブ",
  reviewFilterDone: "完了",
  reviewFilterDismissed: "却下済み",
  reviewSidebarOverallFeedback: "全体的なフィードバック",
  reviewSidebarCommentsPrefix: "コメント（",
  reviewSidebarCommentsRemainingSuffix: " 件 残り）",
  reviewRemainingSuffix: " 件 残り",
  reviewDownload: "ダウンロード",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "印刷 / PDF",
  reviewHidePaper: "論文を非表示",
  reviewShowPaper: "論文を表示",
  reviewCopied: "コピーしました",
  reviewShare: "共有",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "ドラッグして論文パネルのサイズを変更",
  reviewResizeTitle: "ドラッグしてサイズ変更",
  reviewOfPrefix: "レビュー対象: ",
  reviewMetaModel: "モデル",
  reviewMetaDate: "日付",
  reviewMetaDomain: "分野",
  reviewMetaTime: "所要時間",
  reviewMetaCost: "費用",
  reviewMetaReviewLanguage: "レビューの言語",
  reviewMetaAutoDetectedSuffix: " · 自動検出",
  reviewOverallFeedbackHeading: "全体的なフィードバック",
  reviewDetailedCommentsPrefix: "詳細なコメント（",
  reviewDetailedCommentsSuffix: "）",
  reviewGeneratedByPrefix: "生成: ",
  reviewGeneratedBySuffix: "。もちろんです。",
  reviewShareThisReview: "このレビューを共有",
  reviewDeleteReview: "レビューを削除",
  reviewDeleteConfirmHeading: "レビューを削除しますか？",
  reviewDeleteConfirmBody: "本当によろしいですか？結果を確認できなくなります。",
  reviewDeleting: "削除中...",
  reviewYesDelete: "はい、削除します",
  reviewGoBack: "戻る",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "この指摘は本当に正しいですか？",
  chatExamplePrompt2: "これに対処するにはどのように修正すべきですか？",
  chatExamplePrompt3: "論文のどこに当てはまりますか？",
  chatNoResponse: "モデルから応答がありませんでした。もう一度お試しいただくか、モデルを切り替えてください。",
  chatSessionExpired: "OpenRouter のセッションが期限切れになりました。続けるにはもう一度ログインしてください。",
  chatSomethingWrong: "問題が発生しました。",
  chatDiscussKicker: "相談 · ",
  chatKickerComment: "コメント #",
  chatKickerOverallFeedback: "全体的なフィードバック",
  chatDiscussAriaPrefix: "相談: ",
  chatCloseAriaLabel: "チャットを閉じる",
  chatDisconnectKeyTitle:
    "OpenRouter キーの接続を解除する（このタブ以外には保存されません）",
  chatDisconnectKey: "キーの接続を解除",
  chatInputPlaceholder: "このコメントについて質問する…",
  chatMessageAriaLabel: "メッセージ",
  chatStop: "停止",
  chatSend: "送信",
  chatModelDisclosurePrefix: "モデル: ",
  chatKeyGateIntro:
    "OpenRouter に接続すると、このコメントについて相談できます。キーは OpenRouter に直接送信され（当社のサーバーには送信されません）、このタブを閉じると消去されます。",
  chatKeyGateOrPaste: "— またはキーを貼り付け —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "OpenRouter API キー",
  chatKeyGateUseKey: "キーを使用",
  chatKeyGateHelper:
    "OAuth キーはこのタブ内にのみ保持され、タブを閉じると消去されます。当社のサーバーには一切保存されません。",
  chatEmptyHintPrefix: "このコメントについて何でも質問してください。各メッセージは ",
  chatEmptyHintFullPaper: "論文全体",
  chatEmptyHintQuotedPassage: "引用箇所とフィードバック",
  chatEmptyHintSuffix: " をコンテキストとして送信し、あなたの OpenRouter クレジットで実行されます。",
  chatEmptyHintNoPaper:
    "このレビューでは論文の全文が保存されていないため、回答は引用箇所とフィードバックのみに基づきます。",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "開きました: ",
  handoffMenuOpenedPromptMid: " を開き、プロンプトを事前入力しました — coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md を添付して送信してください。（念のため、プロンプトもコピーしてあります。）",
  handoffMenuOpenedPlainMid: " — coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md を添付し、コピーしたプロンプトを貼り付けてください。",
  handoffMenuButtonTitle:
    "論文 + レビューをご自身の AI チャット（Claude、ChatGPT、Gemini、Grok、DeepSeek）に送信",
  handoffMenuButton: "あなたの AI と相談",
  handoffMenuDownloadsIntro: "論文 + レビューをダウンロードしてから、次を開きます:",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "論文",
  paperPanelDownload: "ダウンロード",
  paperPanelDownloadAriaLabel: "論文の Markdown をダウンロード",
  paperPanelCloseAriaLabel: "論文パネルを閉じる",

  // setup page (setup/page.tsx)
  // setup page — tab switcher
  setupTablistAriaLabel: "セットアップの方法",
  setupTabOpenRouter: "OpenRouter キー",
  setupTabSubscription: "自分のサブスクリプションを使う",
  // setup page — OpenRouter tab intro
  setupOrHeading: "OpenRouter キーを取得する",
  setupOrIntro:
    "所要時間は約 2 分です。開始するにはクレジットカードと ~$1 のクレジットが必要です — ステップ 2 で $20 までチャージします。",
  setupOrFasterLabel: "より速い方法:",
  setupOrFasterMid1: " メインのフォームで ",
  setupOrFasterLogIn: "「OpenRouter でログイン」",
  setupOrFasterSuffix:
    " をクリックすると、coarse を認可して手動でのキー作成をスキップできます。それでもクレジットのある OpenRouter アカウントは必要で（下記のステップ 1 と 2）、キーごとの利用上限を設定することを引き続きおすすめします（ステップ 4）。",
  // setup page — OpenRouter step 1
  setupOrStep1Title: "アカウントを作成する",
  setupOrStep1BodyPrefix: "次にアクセスして ",
  setupOrStep1BodySuffix: " 「Get API Key」をクリックするか、Google / GitHub でサインアップしてください。",
  setupOrStep1Annotation: "ホームページ",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "LLM のための統合 API — 1 つのキーで多数のモデルを。",
  // setup page — OpenRouter step 2
  setupOrStep2Title: "クレジットを追加する",
  setupOrStep2BodyPrefix: "次に移動して ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    "。少なくとも $20 を追加してください。安価なオープンソースモデルは 1 回のレビューあたり ~$0.25 ですが、Claude Opus や GPT-5 のような最先端モデルは長い論文では $5–$10 かかることがあります。投稿前に表示される費用見積もりはおおよその目安であり、上限ではありません。余裕を持たせないと、レビューが途中でキーを使い切って失敗することがあります。未使用のクレジットは失効しません。",
  setupOrStep2Annotation: "クレジットページ",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "金額",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "残高: $0.00",
  // setup page — OpenRouter step 3
  setupOrStep3Title: "API キーを作成する",
  setupOrStep3BodyPrefix: "次にアクセスして ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: "「Create Key」をクリックし、次の名前を付けてください ",
  setupOrStep3BodySuffix: "。",
  setupOrStep3Provisioning:
    "それが通常の API キーであることを確認してください — インテグレーションのセクションにあるプロビジョニング/管理用キーではありません。プロビジョニングキーは他のキーの作成や一覧表示はできますが推論を実行できず、それを貼り付けると coarse は「User not found」で失敗します。",
  setupOrStep3CopyWarning: "今すぐキーをコピーしてください — 二度と表示されません。",
  setupOrStep3Annotation: "キーページ",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "キー名",
  setupOrStep3MockYourKey: "あなたのキー",
  // setup page — OpenRouter step 4
  setupOrStep4Title: "キーに利用上限を設定する",
  setupOrStep4BodyPrefix: "次の場所で ",
  setupOrStep4BodyLink: "Keys ページ",
  setupOrStep4BodyMid1: "新しいキーの横にある ",
  setupOrStep4BodyMid2: " メニューをクリックし、「Edit」を選んで、クレジット上限を次のように設定してください ",
  setupOrStep4BodyAtLeast: "少なくとも $20",
  setupOrStep4BodySuffix:
    "。上限に達するとキーは動作を停止するため、想定外の請求が発生することはありません。ただし、設定が厳しすぎると、1 回の高額なレビューで途中で使い切ることがあります。",
  setupOrStep4Annotation: "キーメニュー",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "このキーのクレジット上限",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "これが重要な理由:",
  setupOrStep4WhyMid1: " coarse はオープンソースです — ",
  setupOrStep4WhyLink: "すべてのコードを読む",
  setupOrStep4WhySuffix:
    "ことができます。あなたのキーはレビューを実行するために OpenRouter に直接送信され、その後破棄されます — 保存されることはありません。しかし当社を信用する必要はありません。キーごとの上限により、最悪の場合でも、あなたが許可した以上に使われることは決してないと保証されます。",
  setupOrStep4CostLabel: "費用見積もりに関する注意:",
  setupOrStep4CostBody:
    " 投稿前に表示される見積もりは ~15% のバッファを持つヒューリスティックであり、確固たる上限ではありません。最先端モデルで長い論文の場合、証明の検証や批評の書き直しが始まると、実際の費用は見積もりの ~2 倍まで達することがあります。キーごとの上限が見積もりちょうどに設定されていると、難しいレビュー 1 回でそれを使い切って途中で失敗することがあります。常に余裕を持たせてください。",
  // setup page — OpenRouter step 5
  setupOrStep5Title: "coarse に貼り付ける",
  setupOrStep5Body: "ここに戻ってきて、キーをフォームに貼り付け、PDF をアップロードしてください。",
  setupOrStep5Annotation: "coarse フォーム",
  setupOrStep5MockEmail: "メール",
  setupOrStep5MockKey: "OpenRouter キー",
  setupOrStep5MockButton: "論文をレビューする",
  // setup page — shared footer CTA
  setupReadyCta: "準備はいいですか？論文をレビューする →",
  // setup page — subscription tab intro
  setupSubHeading: "コーディングエージェントのサブスクリプションを使う",
  setupSubIntro1:
    "すでに Claude Code、Codex、または Gemini CLI に料金を支払っているユーザー向けです。レビューはあなたのサブスクリプションで実行され、そこに課金されます。OCR パスのために OpenRouter に ~$0.15 をお支払いいただくだけです。",
  setupSubIntro2:
    "ご自身の Claude Code、Codex、または Gemini CLI アカウントを使用して、ご自身のマシン上でローカルに実行されます。coarse.ink はあなたのプロバイダーのログイン情報を受信または保存しません。お使いのプロバイダーの利用規約と利用上限は引き続き適用されます。coarse.ink は Anthropic、OpenAI、Google とは提携していません。",
  // setup page — subscription step 1
  setupSubStep1Title: "コーディングエージェントをインストールする",
  setupSubStep1Body:
    "お支払いになっているものをどれでも選んでください。支払っていない場合は、Gemini CLI に無料枠があります。ベンダー自身のページからインストールしてください — そちらのドキュメントは最新の状態に保たれています。",
  setupSubStep1ClaudePrice: "Anthropic Pro または Max",
  setupSubStep1CodexPrice: "ChatGPT Plus、Pro、または Business",
  setupSubStep1GeminiPrice: "無料枠でほとんどの論文に対応できます",
  setupSubStep1InstallLabel: "インストール手順 ↗",
  setupSubStep1Verify:
    "テストコマンドを実行して、インストールとログインを確認してください。応答が表示されれば、準備完了です。",
  setupSubStep1CardLogin: "ログイン: ",
  setupSubStep1CardTest: "テスト: ",
  // setup page — subscription step 2
  setupSubStep2Title: "OpenRouter キーをマシンに用意する（PDF のみ）",
  setupSubStep2BodyPrefix:
    "このステップは PDF の論文にのみ当てはまります — PDF 以外のソース（.tex, .md, .docx, …）は OCR なしでローカルに抽出されるため、どこにも OpenRouter キーは不要で、ステップ 3 にそのまま進めます。PDF の場合、coarse は OCR ステップ（1 論文あたり ~$0.10）のために引き続き OpenRouter を必要とします。次に従ってください ",
  setupSubStep2BodyTab: "OpenRouter キー",
  setupSubStep2BodySuffix:
    " のタブで、アカウントを作成し、$1 のクレジットを追加して、キーごとに $2 の上限を設定してください。OpenRouter 単独の方法で必要だった $20 のバッファはここでは不要です。レビュー自体はあなたのコーディングエージェントのサブスクリプションで実行されるためです。",
  setupSubStep2KeyPrefix: "次に、キーをご自身のマシンに用意してください: 次を実行するか ",
  setupSubStep2KeyMid1: "次に保存するか ",
  setupSubStep2KeyMid2: "または次に保存してください ",
  setupSubStep2KeySuffix:
    "。抽出を実行するとき、CLI はそれをローカルで読み取ります。coarse.ink がそれを目にすることは決してありません。",
  // setup page — subscription step 3
  setupSubStep3Title: "論文をアップロードし、CLI を選ぶ",
  setupSubStep3BodyPrefix: "次の場所で ",
  setupSubStep3BodyLink: "メインページ",
  setupSubStep3BodyMid: "論文（PDF, .tex, .md, .docx, …）をフォームにドロップし、次をクリックしてください ",
  setupSubStep3BodyButton: "自分のサブスクリプションでレビュー ▾",
  setupSubStep3BodySuffix:
    " のドロップダウンを開いて CLI を選んでください。coarse はファイルをアップロードし、引き継ぎトークンを発行し、次のステップで貼り付けるプロンプトを表示します。ここではフォームに OpenRouter キーを貼り付けません。CLI があなたのマシンからそれを読み取ります（ステップ 2）。",
  // setup page — subscription step 4
  setupSubStep4Title: "プロンプトを CLI に貼り付ける",
  setupSubStep4BodyPrefix: "coarse は自然言語のプロンプトを 1 つお渡しします。パネルからそれをコピーし、次の ",
  setupSubStep4BodyMid1: "、 ",
  setupSubStep4BodyMid2: "、または ",
  setupSubStep4BodyMid3: " のセッションに貼り付け、送信を押してください。エージェントはスキルバンドルを更新し、独自のサブプロセス呼び出しで完全な coarse パイプラインを実行し、完了すると次を表示します ",
  setupSubStep4BodySuffix:
    " の URL です。所要時間は 10–25 分です。その URL をクリックすると、coarse.ink で完成したレビューが開きます。",
  setupSubStep4TimeoutLabel: "コーディングエージェントに貼り付ける場合",
  setupSubStep4TimeoutSuffix:
    " (プレーンなターミナルではない場合)、プロンプトを送信する前に、その bash ツールのタイムアウトを少なくとも 45 分まで引き上げてください。エージェントのデフォルトのタイムアウトは 2 分ほどと短いことがあり、10–25 分のレビュー実行時間を大きく下回ります。",
  // setup page — subscription step 5 (troubleshooting)
  setupSubStep5Title: "うまくいかない場合",
  setupSubTrouble1Symptom: "「Try opening Claude Code / Codex」ボタンを押しても何も起こらない。",
  setupSubTrouble1Fix:
    "このボタンはデスクトップアプリがインストールされている場合にのみ動作します。CLI のみのインストールでは、ブラウザがあなたのためにターミナルを起動できません。パネルからプロンプトをコピーし、手動で CLI に貼り付けてください。",
  setupSubTrouble2Symptom: "エージェントの実行中に「No such command ‘install-skills’」が表示される。",
  setupSubTrouble2FixPrefix: "無視して問題ありません。スキルバンドルは引き続き次を通じて直接読み込まれます ",
  setupSubTrouble2FixSuffix: "。エージェントはレビューのステップへと続行します。",
  setupSubTrouble3Symptom: "レビュー後に Anthropic / OpenAI / Google の請求が増えた。",
  setupSubTrouble3FixPrefix: "次を確認してください ",
  setupSubTrouble3FixMid1: "、 ",
  setupSubTrouble3FixMid2: "、または ",
  setupSubTrouble3FixSuffix:
    " がシェル環境にないか。設定されていると、ホスト CLI はあなたのサブスクリプションではなく API アカウントに課金します。v1.3.0 以降はこれらを自動的に取り除きますが、それ以前のバージョンでは行いませんでした。",
  setupSubTrouble4Symptom: "コメントがいつもより少ない（15–25 件ではなく ~10 件）。",
  setupSubTrouble4FixPrefix: "あるセクションが 30 分のタイムアウトに達して除外されました。デフォルトの強度ではまれですが、次の場合に起きやすくなります ",
  setupSubTrouble4FixSuffix:
    " 長い論文の場合です。再実行してください。2 回起きるようなら強度を 1 段階下げてください。",

  // compare page (ComparePage.tsx)
  comparePanelErrorBody: "これは表示できませんでした。別のモデルか比較をお試しください。",
  comparePaperCorticalCircuits: "皮質回路",
  comparePaperCosetCodes: "剰余類符号",
  comparePaperPopulationGenetics: "集団遺伝学",
  comparePaperTargetingInterventions: "介入のターゲティング",
  compareScoresShow: "表示",
  compareScoresHide: "非表示",
  compareScoresToggleSuffix: " 全論文にわたるすべてのスコア ",
  compareScoresColPaper: "論文",
  compareScoresColReference: "リファレンス",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "Gemini 3.1 Pro が PDF のマルチモーダル入力で評価しました。5.0/5 = リファレンスと同等の品質。5.5+/5 = それを上回ります。",
  compareJudgeShow: "表示",
  compareJudgeHide: "非表示",
  compareJudgeToggleSuffix: " Gemini 3.1 Pro に送信された判定プロンプト ",
  compareJudgeExplain:
    "既知の LLM-as-judge バイアスを軽減するため、判定は評価ごとに 2 回実行され、2 つのレビューを提示順で入れ替え、両方の順序でスコアを平均します。これは、判定者が先に表示されたレビューを体系的に優遇する位置バイアスを打ち消します。プロンプトには、冗長性バイアス（中身よりも長さを評価しない）、自信バイアス（適切なヘッジングよりも断定的な言い回しを評価しない）、権威バイアス（正確さよりも専門用語や引用数を評価しない）、寛大さバイアス（中間に偏らず 1〜6 の全スコア範囲を使う）を打ち消すための具体的な指示も含まれています。レビューは出自に基づくスコアリングを防ぐため、「リファレンス」や「生成」ではなく中立的に「レビュー A」「レビュー B」とラベル付けされます。",
  compareJudgeSystemPromptLabel: "システムプロンプト",
  compareJudgeUserPromptLabel: "ユーザープロンプト（論文 + レビューは実行時に挿入されます）",
  compareVsMid: " 対 ",
  compareScoreOutOf: "/5",
  compareMetricCoverage: "カバレッジ",
  compareMetricSpecificity: "具体性",
  compareMetricDepth: "深さ",
  compareJumpTo: "ジャンプ先",
  compareSectionOverallFeedback: "全体的なフィードバック",
  compareSectionDetailedComments: "詳細なコメント",
  compareVisitPrefix: "次にアクセス ",
  comparePdfReviewSuffix: " のレビュー",
  comparePdfFallback: "iframe が表示されない場合は PDF をダウンロードしてください ↓",
};
