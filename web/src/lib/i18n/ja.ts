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
};
