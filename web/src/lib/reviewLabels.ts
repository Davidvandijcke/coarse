// Localized review-markdown labels — TS mirror of src/coarse/review_labels.py.
// Read by the legacy markdown parser (parseReview.ts) so it can still parse a
// review rendered in a non-English language. Keep in sync with the Python
// catalog (codes, keys, and values); tests/test_web_i18n_contract.py guards it.
//
// New localized reviews render from result_json on the web, so this parser path
// is mainly the legacy/CLI fallback — but a localized review that lacks
// result_json must still parse, hence the mirror.

export interface ReviewLabels {
  date: string;
  domain: string;
  taxonomy: string;
  filter: string;
  active_comments: string;
  overall_feedback: string;
  overall_intro: string;
  outline: string;
  recommendation: string;
  revision_targets: string;
  status: string;
  pending: string;
  detailed_comments: string;
  quote: string;
  feedback: string;
}

const EN: ReviewLabels = {
  date: "Date",
  domain: "Domain",
  taxonomy: "Taxonomy",
  filter: "Filter",
  active_comments: "Active comments",
  overall_feedback: "Overall Feedback",
  overall_intro: "Here are some overall reactions to the document.",
  outline: "Outline",
  recommendation: "Recommendation",
  revision_targets: "Key revision targets",
  status: "Status",
  pending: "Pending",
  detailed_comments: "Detailed Comments",
  quote: "Quote",
  feedback: "Feedback",
};

const LABELS: Record<string, ReviewLabels> = {
  en: EN,
  es: {
    date: "Fecha",
    domain: "Dominio",
    taxonomy: "Taxonomía",
    filter: "Filtro",
    active_comments: "Comentarios activos",
    overall_feedback: "Valoración general",
    overall_intro: "Estas son algunas reacciones generales al documento.",
    outline: "Resumen",
    recommendation: "Recomendación",
    revision_targets: "Objetivos clave de revisión",
    status: "Estado",
    pending: "Pendiente",
    detailed_comments: "Comentarios detallados",
    quote: "Cita",
    feedback: "Comentarios",
  },
  fr: {
    date: "Date",
    domain: "Domaine",
    taxonomy: "Taxonomie",
    filter: "Filtre",
    active_comments: "Commentaires actifs",
    overall_feedback: "Évaluation générale",
    overall_intro: "Voici quelques réactions générales au document.",
    outline: "Résumé",
    recommendation: "Recommandation",
    revision_targets: "Objectifs clés de révision",
    status: "Statut",
    pending: "En attente",
    detailed_comments: "Commentaires détaillés",
    quote: "Citation",
    feedback: "Commentaire",
  },
  de: {
    date: "Datum",
    domain: "Fachgebiet",
    taxonomy: "Taxonomie",
    filter: "Filter",
    active_comments: "Aktive Kommentare",
    overall_feedback: "Gesamtbewertung",
    overall_intro: "Hier sind einige allgemeine Anmerkungen zum Dokument.",
    outline: "Zusammenfassung",
    recommendation: "Empfehlung",
    revision_targets: "Zentrale Überarbeitungsziele",
    status: "Status",
    pending: "Ausstehend",
    detailed_comments: "Detaillierte Kommentare",
    quote: "Zitat",
    feedback: "Anmerkung",
  },
  nl: {
    date: "Datum",
    domain: "Vakgebied",
    taxonomy: "Taxonomie",
    filter: "Filter",
    active_comments: "Actieve opmerkingen",
    overall_feedback: "Algemene beoordeling",
    overall_intro: "Hier zijn enkele algemene reacties op het document.",
    outline: "Samenvatting",
    recommendation: "Aanbeveling",
    revision_targets: "Belangrijkste revisiedoelen",
    status: "Status",
    pending: "In behandeling",
    detailed_comments: "Gedetailleerde opmerkingen",
    quote: "Citaat",
    feedback: "Opmerking",
  },
  pt: {
    date: "Data",
    domain: "Domínio",
    taxonomy: "Taxonomia",
    filter: "Filtro",
    active_comments: "Comentários ativos",
    overall_feedback: "Avaliação geral",
    overall_intro: "Aqui estão algumas reações gerais ao documento.",
    outline: "Resumo",
    recommendation: "Recomendação",
    revision_targets: "Principais objetivos de revisão",
    status: "Estado",
    pending: "Pendente",
    detailed_comments: "Comentários detalhados",
    quote: "Citação",
    feedback: "Comentário",
  },
  it: {
    date: "Data",
    domain: "Dominio",
    taxonomy: "Tassonomia",
    filter: "Filtro",
    active_comments: "Commenti attivi",
    overall_feedback: "Valutazione complessiva",
    overall_intro: "Ecco alcune reazioni generali al documento.",
    outline: "Sintesi",
    recommendation: "Raccomandazione",
    revision_targets: "Obiettivi chiave di revisione",
    status: "Stato",
    pending: "In sospeso",
    detailed_comments: "Commenti dettagliati",
    quote: "Citazione",
    feedback: "Commento",
  },
  "zh-Hans": {
    date: "日期",
    domain: "领域",
    taxonomy: "分类",
    filter: "筛选",
    active_comments: "活动评论",
    overall_feedback: "总体评价",
    overall_intro: "以下是对该文档的一些总体反馈。",
    outline: "概要",
    recommendation: "建议",
    revision_targets: "主要修改目标",
    status: "状态",
    pending: "待处理",
    detailed_comments: "详细评论",
    quote: "引文",
    feedback: "反馈",
  },
  "zh-Hant": {
    date: "日期",
    domain: "領域",
    taxonomy: "分類",
    filter: "篩選",
    active_comments: "使用中的評論",
    overall_feedback: "總體評價",
    overall_intro: "以下是對該文件的一些總體回饋。",
    outline: "概要",
    recommendation: "建議",
    revision_targets: "主要修改目標",
    status: "狀態",
    pending: "待處理",
    detailed_comments: "詳細評論",
    quote: "引文",
    feedback: "回饋",
  },
  ja: {
    date: "日付",
    domain: "分野",
    taxonomy: "分類",
    filter: "フィルター",
    active_comments: "アクティブなコメント",
    overall_feedback: "総合評価",
    overall_intro: "本文書に対する全体的な所見は以下のとおりです。",
    outline: "概要",
    recommendation: "推奨",
    revision_targets: "主要な改訂目標",
    status: "ステータス",
    pending: "保留中",
    detailed_comments: "詳細なコメント",
    quote: "引用",
    feedback: "フィードバック",
  },
  ko: {
    date: "날짜",
    domain: "분야",
    taxonomy: "분류",
    filter: "필터",
    active_comments: "활성 코멘트",
    overall_feedback: "종합 평가",
    overall_intro: "다음은 이 문서에 대한 전반적인 의견입니다.",
    outline: "개요",
    recommendation: "권고",
    revision_targets: "주요 수정 목표",
    status: "상태",
    pending: "대기 중",
    detailed_comments: "상세 코멘트",
    quote: "인용",
    feedback: "피드백",
  },
  ar: {
    date: "التاريخ",
    domain: "المجال",
    taxonomy: "التصنيف",
    filter: "التصفية",
    active_comments: "التعليقات النشطة",
    overall_feedback: "التقييم العام",
    overall_intro: "فيما يلي بعض الملاحظات العامة على المستند.",
    outline: "ملخص",
    recommendation: "التوصية",
    revision_targets: "أهداف المراجعة الرئيسية",
    status: "الحالة",
    pending: "قيد الانتظار",
    detailed_comments: "تعليقات مفصلة",
    quote: "اقتباس",
    feedback: "ملاحظة",
  },
};

/** Labels for a language code; English for unknown/empty. */
export function reviewLabels(code: string | null | undefined): ReviewLabels {
  if (!code) return EN;
  return LABELS[code] ?? EN;
}
