// Japanese (ja) site-UI catalog. Mirrors the keys of ./en.ts exactly; only the
// values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const ja: Messages = {
  siteLanguageLabel: "サイトの言語",

  codeBlockCopied: "コピーしました ✓",
  codeBlockCopy: "コピー",

  headerTagline: "査読は公共財です。",
  navSetup: "セットアップ",
  navSideBySide: "比較",
  navGithub: "github ↗",

  bannerPausedDefault: "投稿は一時的に停止しています。",
  bannerBusyPrefix: "システムが混雑しています（",
  bannerBusySuffix: " 件のスロットを使用中）。レビューは待機列に入る場合があります。",
  bannerFasterPrefix: "より速く結果を得るには、CLI をお使いください:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "ねえ ",
  heroGreetingSuffix: " この論文をレビューしてもらえますか？",
  heroHeading: "‘coarse!",
  heroLede:
    "AI エージェントがあなたの論文をレビューし、査読レポートを作成します。API の費用は直接お支払いいただきます。アカウントは不要です。",
  heroManifesto:
    "学術的な査読は、無償の学術労働に支えられています。他社はそれをビジネスにすることにしました。私たちはそれを良しとしませんでした。",

  scoreVsOthers: "他の AI レビュアーとの比較",
  statCostNum: "< $2*",
  statCostLabel: "1 回のレビューあたり",
  statCostFootnote: "*通常は :)",
  statCommentsNum: "20+",
  statCommentsLabel: "詳細なコメント",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "オープンソース",

  comparePrefix: "ブラインド評価の対象:",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "カバレッジ、具体性、深さでより高いスコアを獲得 -- しかもごくわずかな費用で。",
  compareLink: "比較を見る →",

  formSubmitHeading: "論文を投稿する",
  fieldPaper: "論文",
  dropzoneAriaLabel: "論文をアップロード — ファイルをドロップするかクリックして選択してください",
  dropzoneInputAriaLabel: "アップロードするファイルを選択",
  dropzoneReplaceSuffix: " MB — クリックまたはドロップで置き換え",
  dropzonePromptPrefix: "ここにファイルをドロップ、または ",
  dropzoneBrowse: "参照",
  dropzoneMaxSize: "最大 50 MB",

  fieldEmail: "メール ",
  fieldEmailQualifier: "（ウェブレビューのみ）",
  emailPlaceholderUnavailable: "— 利用できません —",
  emailPlaceholder: "you@university.edu",
  emailAriaLabel: "メールアドレス",
  emailHelperDisabled:
    "メール配信は一時的に停止しています。投稿時にレビューキーを保存し、1 時間ほど後にもう一度ご確認ください。",
  emailHelperPrefix:
    "完了したらメールでお知らせします。届かない場合は迷惑メールフォルダーをご確認ください。",

  fieldKey: "OpenRouter キー",
  fieldKeyGetOne: "取得する →",
  keyOrPaste: "— またはキーを貼り付け —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "OpenRouter API キー",
  keyHelper:
    "OAuth キーはこのタブ内にのみ保持され、タブを閉じると消去されます。当社のサーバーには一切保存されません。",

  fieldNotes: "レビュアーへのメモ",
  fieldNotesOptional: "（任意）",
  notesPlaceholder:
    "例: §3 の識別戦略に注目してください — データのセクションはまだ仮のものです。",
  notesAriaLabel: "レビュアーを誘導するための任意のメモ",
  notesHelper: "レビュアーが注目する点を誘導します。ルーブリックを上書きするものではありません。",

  costEstimating: "費用を見積もっています...",
  costEstimatePrefix: "推定 API 費用: $",
  costUnavailable: "このモデルでは費用の見積もりを利用できません",

  turnstileFailedLine1Prefix:
    "人間確認を完了できませんでした。何かが次をブロックまたは遅延させています ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — 多くの場合、ブラウザの厳格なプライバシーモード（Safari のトラッキング防止や Firefox ETP の厳格設定など）、コンテンツ/広告ブロッカー（Brave Shields、一部のリストでの uBlock Origin）、または遅いもしくはフィルタリングされたネットワークが原因です。",
  turnstileFailedLine2Prefix: "まずページの再読み込みをお試しください。それでも解決しない場合は、 ",
  turnstileFailedLine2Mid: " を ",
  turnstileFailedLine2Suffix:
    " に対して許可してください（コンテンツブロッカーを無効にするかプライバシー設定を緩める）。または別のブラウザをお使いください。プレビュー URL では、そのホスト名を Cloudflare Turnstile ウィジェットの許可リストにデプロイ側で追加する必要がある場合もあります。",
  turnstileFailedLine3Prefix: "または、ご自身の OpenRouter キーで coarse をローカルで実行してください: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: "。",

  submitButton: "論文をレビューする",
  submitButtonBusy: "送信中...",
  submitOr: "または",
  handoffButton: "自分のサブスクリプションでレビュー ▾",
  handoffButtonBusy: "準備中...",

  handoffUploading: "論文をアップロード中...",
  handoffPreparing: "引き継ぎを準備中...",

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
    "ローカルの Mistral OCR ステップ（ご自身の OpenRouter キーを使用）に対して ~$0.10 をお支払いいただくだけです。PDF 以外のアップロード（.tex, .md, .docx, …）は OCR をスキップし、OpenRouter キーは不要です。",
  explainSubscriptionNonPdf:
    "ファイルが PDF ではないため、Mistral OCR ステップは完全にスキップされます — 実行全体がサブスクリプションでカバーされ、OpenRouter キーは不要です。",
  explainSubscriptionPart3: "レビューは完了するとこのページに表示されます。",
  explainDisclaimer:
    "ご自身の Claude Code、Codex、または Gemini CLI アカウントを使用して、ご自身のマシン上でローカルに実行されます。coarse.ink はあなたのプロバイダーのログイン情報を受信または保存することはなく、お使いのプロバイダーの利用規約、利用上限、組織のポリシーが適用されます。coarse.ink は Anthropic、OpenAI、または Google とは提携していません。",

  handoffReviewWithPrefix: "レビューに使用: ",
  handoffModelLabel: "モデル",
  handoffEffortLabel: "労力",
  handoffPastePromptPrefix: "このプロンプトを次のターミナルに貼り付けてください: ",
  handoffPastePromptSuffix: " ターミナル:",
  handoffRunHint:
    "エージェントは coarse-review スキルを更新し、完全なレビューをローカルで実行します。所要時間は 10–25 分です。プロバイダーのログイン情報はあなたのマシン上に留まります。",
  handoffKeyNeededPrefix:
    "まず OpenRouter キーをあなたのマシンに用意する必要があります — 次をエクスポートしてください ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: "、または次に設定してください ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " か ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    "。引き継ぎ URL はエージェントのチャットログに残るため、ブラウザ経由では送信しません。キーがない場合、エージェントが尋ねます。",
  handoffKeyNotNeeded:
    "この論文には OpenRouter キーは不要です — PDF ではないため、抽出は Mistral OCR ステップなしでローカルに実行されます。",
  handoffReviewUrlIntro: "レビューが完了すると、次に表示されます:",
  handoffInstallPrefix: "まだ ",
  handoffInstallSuffix: " をお持ちでないですか？ ",
  handoffInstallLink: "インストールする →",

  findReviewHeading: "レビューを探す",
  findReviewPlaceholder: "レビューキー、完全なレビューリンク、または従来のレビュー ID を貼り付けてください...",
  findReviewAriaLabel: "レビューキー",
  findReviewButton: "検索",

  footerPrivacy: "プライバシー",
  footerTerms: "利用規約",
  footerContact: "お問い合わせ",

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
    "人間確認ウィジェットを読み込めませんでした — ブラウザ拡張機能（Brave Shields、uBlock Origin、Firefox ETP 厳格設定）が challenges.cloudflare.com をブロックしている可能性が高いです。次に対してそれを無効にしてみてください ",
  errorTurnstileBlockedSuffix: "。または coarse をローカルで実行してください: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "人間確認の読み込みをまだ待っています — 少し待ってからもう一度お試しください。",
  errorPrepareUpload: "アップロードの準備に失敗しました",
  errorUploadFailed: "ファイルのアップロードに失敗しました — もう一度お試しください",
  errorSubmissionFailed: "送信に失敗しました",
  errorHandoffFailed: "引き継ぎに失敗しました",
  launchCommandCopied: "コマンドをクリップボードにコピーしました。ターミナルに貼り付けてください。",
  launchOpeningCodex:
    "Codex デスクトップアプリを開いています — コンポーザーに自動入力されるはずです。送信を押してください。",
  launchOpeningPrefix: "開いています ",
  launchOpeningSuffix: " — クリップボードからプロンプトを貼り付けてください（⌘V / Ctrl+V）。",
  launchDidntOpenSuffix:
    " デスクトップアプリが開きませんでした。CLI 版のみをインストールしている場合は、上記のコマンドをターミナルに貼り付けてください。",
  errorLoginCouldNotStartPrefix: "OpenRouter のログインを開始できませんでした: ",

  reviewLanguageLabel: "レビューの言語",
  reviewLanguageAuto: "自動 — 論文の言語に合わせる",
  reviewLanguageHelper:
    "デフォルトでは論文自体の言語を使用します。引用は常に原文のままです。",
};
