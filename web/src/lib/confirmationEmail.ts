// Localized copy for the submit-time "your paper is being reviewed" email.
//
// Keyed on the submitter's site_language — the only language reliably known at
// submit time (review_language may be empty = "follow the detected paper
// language", which the worker only resolves later). English fallback for an
// unknown/empty code.
//
// The sibling "your review is ready" completion email is localized server-side
// in the worker (src/coarse/review_labels.py `_EMAIL`). Keep terminology
// consistent with it (the word for "review", the review-key label, formality).
//
// Templates carry {title} and {model} placeholders; callers substitute them
// (HTML-escaping interpolated values). Plain data module — safe to import from a
// server route (no React/client dependency).

export interface ConfirmationEmailCopy {
  subject: string; // {title}
  greeting: string;
  body: string; // {title}, {model}
  bodyNoModel: string; // {title}
  track: string;
  saveKey: string;
}

const EN: ConfirmationEmailCopy = {
  subject: `Your paper "{title}" is being reviewed`,
  greeting: `Hi,`,
  body: `Your paper "{title}" is being reviewed using {model}. We'll email you when it's done (usually 30–60 minutes).`,
  bodyNoModel: `Your paper "{title}" is being reviewed. We'll email you when it's done (usually 30–60 minutes).`,
  track: `Track progress:`,
  saveKey: `Save your review key:`,
};

const CATALOG: Record<string, ConfirmationEmailCopy> = {
  en: EN,
  es: {
    subject: `Tu artículo "{title}" está en revisión`,
    greeting: `Hola:`,
    body: `Tu artículo "{title}" está en revisión con {model}. Te enviaremos un correo cuando esté lista (normalmente entre 30 y 60 minutos).`,
    bodyNoModel: `Tu artículo "{title}" está en revisión. Te enviaremos un correo cuando esté lista (normalmente entre 30 y 60 minutos).`,
    track: `Sigue el progreso:`,
    saveKey: `Guarda tu clave de la revisión:`,
  },
  fr: {
    subject: `Votre article « {title} » est en cours d'évaluation`,
    greeting: `Bonjour,`,
    body: `Votre article « {title} » est en cours d'évaluation avec {model}. Nous vous enverrons un e-mail dès qu'elle sera terminée (généralement de 30 à 60 minutes).`,
    bodyNoModel: `Votre article « {title} » est en cours d'évaluation. Nous vous enverrons un e-mail dès qu'elle sera terminée (généralement de 30 à 60 minutes).`,
    track: `Suivre la progression :`,
    saveKey: `Enregistrez votre clé de l'évaluation :`,
  },
  de: {
    subject: `Ihr Papier "{title}" wird begutachtet`,
    greeting: `Hallo,`,
    body: `Ihr Papier "{title}" wird gerade mit {model} begutachtet. Wir senden Ihnen eine E-Mail, sobald die Begutachtung abgeschlossen ist (in der Regel 30–60 Minuten).`,
    bodyNoModel: `Ihr Papier "{title}" wird gerade begutachtet. Wir senden Ihnen eine E-Mail, sobald die Begutachtung abgeschlossen ist (in der Regel 30–60 Minuten).`,
    track: `Fortschritt verfolgen:`,
    saveKey: `Speichern Sie Ihren Begutachtungsschlüssel:`,
  },
  nl: {
    subject: `Je artikel "{title}" wordt beoordeeld`,
    greeting: `Hoi,`,
    body: `Je artikel "{title}" wordt beoordeeld met {model}. We sturen je een e-mail zodra de beoordeling klaar is (meestal 30–60 minuten).`,
    bodyNoModel: `Je artikel "{title}" wordt beoordeeld. We sturen je een e-mail zodra de beoordeling klaar is (meestal 30–60 minuten).`,
    track: `Volg de voortgang:`,
    saveKey: `Bewaar je beoordelingssleutel:`,
  },
  pt: {
    subject: `Seu artigo "{title}" está em revisão`,
    greeting: `Olá,`,
    body: `Seu artigo "{title}" está em revisão com {model}. Enviaremos um e-mail quando a revisão estiver pronta (normalmente de 30 a 60 minutos).`,
    bodyNoModel: `Seu artigo "{title}" está em revisão. Enviaremos um e-mail quando a revisão estiver pronta (normalmente de 30 a 60 minutos).`,
    track: `Acompanhe o progresso:`,
    saveKey: `Salve sua chave da revisão:`,
  },
  it: {
    subject: `Il tuo articolo "{title}" è in fase di revisione`,
    greeting: `Ciao,`,
    body: `Il tuo articolo "{title}" è in fase di revisione con {model}. Ti invieremo un'e-mail quando la revisione sarà pronta (di solito tra 30 e 60 minuti).`,
    bodyNoModel: `Il tuo articolo "{title}" è in fase di revisione. Ti invieremo un'e-mail quando la revisione sarà pronta (di solito tra 30 e 60 minuti).`,
    track: `Segui i progressi:`,
    saveKey: `Salva la tua chiave della revisione:`,
  },
  "zh-Hans": {
    subject: `您的论文“{title}”正在评审中`,
    greeting: `您好：`,
    body: `您的论文“{title}”正在使用 {model} 进行评审。评审完成后我们会通过电子邮件通知您（通常需要 30–60 分钟）。`,
    bodyNoModel: `您的论文“{title}”正在评审中。评审完成后我们会通过电子邮件通知您（通常需要 30–60 分钟）。`,
    track: `跟踪进度：`,
    saveKey: `请保存您的评审密钥：`,
  },
  "zh-Hant": {
    subject: `您的論文「{title}」正在評審中`,
    greeting: `您好：`,
    body: `您的論文「{title}」正在使用 {model} 進行評審。評審完成後我們會以電子郵件通知您（通常需要 30–60 分鐘）。`,
    bodyNoModel: `您的論文「{title}」正在評審中。評審完成後我們會以電子郵件通知您（通常需要 30–60 分鐘）。`,
    track: `追蹤進度：`,
    saveKey: `請保存您的評審金鑰：`,
  },
  ja: {
    subject: `論文「{title}」を現在レビューしています`,
    greeting: `こんにちは。`,
    body: `論文「{title}」を {model} を使用してレビューしています。完了しましたらメールでお知らせします（通常30〜60分かかります）。`,
    bodyNoModel: `論文「{title}」を現在レビューしています。完了しましたらメールでお知らせします（通常30〜60分かかります）。`,
    track: `進捗を確認する：`,
    saveKey: `レビューキーを保存してください：`,
  },
  ko: {
    subject: `논문 "{title}"을(를) 검토하고 있습니다`,
    greeting: `안녕하세요,`,
    body: `{model}을(를) 사용하여 논문 "{title}"을(를) 검토하고 있습니다. 리뷰가 완료되면 이메일로 알려드리겠습니다(보통 30~60분 소요됩니다).`,
    bodyNoModel: `논문 "{title}"을(를) 검토하고 있습니다. 리뷰가 완료되면 이메일로 알려드리겠습니다(보통 30~60분 소요됩니다).`,
    track: `진행 상황 확인하기:`,
    saveKey: `리뷰 키를 저장하세요:`,
  },
  ar: {
    subject: `تجري حاليًا مراجعة بحثك "{title}"`,
    greeting: `مرحبًا،`,
    body: `تجري حاليًا مراجعة بحثك "{title}" باستخدام {model}. سنرسل إليك رسالة بريد إلكتروني عند اكتمال المراجعة (عادةً من 30 إلى 60 دقيقة).`,
    bodyNoModel: `تجري حاليًا مراجعة بحثك "{title}". سنرسل إليك رسالة بريد إلكتروني عند اكتمال المراجعة (عادةً من 30 إلى 60 دقيقة).`,
    track: `تابع التقدم:`,
    saveKey: `احفظ مفتاح المراجعة:`,
  },
};

/**
 * Localized confirmation-email copy for a stored language code. Accepts exact
 * codes ("nl", "zh-Hant") and falls back to the base language for region/script
 * variants ("pt-BR" → "pt", bare "zh" → "zh-Hans"); English for unknown/empty.
 */
export function confirmationEmailCopy(code: string | null | undefined): ConfirmationEmailCopy {
  const trimmed = (code ?? "").trim();
  if (trimmed in CATALOG) return CATALOG[trimmed];
  const base = trimmed.split("-")[0].toLowerCase();
  if (base === "zh") return CATALOG["zh-Hans"];
  if (base in CATALOG) return CATALOG[base];
  return EN;
}
