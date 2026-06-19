"""Localized labels for the rendered review markdown.

Single source of truth for the human-facing structural labels that
``synthesis.render_review`` emits, keyed by language code. The TypeScript mirror
is ``web/src/lib/reviewLabels.ts`` (read by the legacy markdown parser so it can
still parse a localized review); ``tests/test_web_i18n_contract.py`` guards that
the two stay in sync.

English is the fallback for any language not in the table, and the English
values are byte-identical to the pre-localization literals so an English review
renders exactly as before.
"""

from __future__ import annotations

# Label keys used by render_review. Keep this list and the per-language dicts in
# sync (a test asserts every language defines exactly these keys).
_LABEL_KEYS = (
    "date",  # "Date" field label
    "domain",  # "Domain" field label
    "taxonomy",  # "Taxonomy" field label
    "filter",  # "Filter" field label
    "active_comments",  # "Active comments" filter value
    "overall_feedback",  # "Overall Feedback" H2
    "overall_intro",  # "Here are some overall reactions to the document."
    "outline",  # "Outline" sub-label
    "recommendation",  # "Recommendation" label
    "revision_targets",  # "Key revision targets" label
    "status",  # "Status" label
    "pending",  # "Pending" status value
    "detailed_comments",  # "Detailed Comments" H2 (count appended in parens)
    "quote",  # "Quote" label
    "feedback",  # "Feedback" label
)

_EN: dict[str, str] = {
    "date": "Date",
    "domain": "Domain",
    "taxonomy": "Taxonomy",
    "filter": "Filter",
    "active_comments": "Active comments",
    "overall_feedback": "Overall Feedback",
    "overall_intro": "Here are some overall reactions to the document.",
    "outline": "Outline",
    "recommendation": "Recommendation",
    "revision_targets": "Key revision targets",
    "status": "Status",
    "pending": "Pending",
    "detailed_comments": "Detailed Comments",
    "quote": "Quote",
    "feedback": "Feedback",
}

# Per-language overrides. Each must define exactly _LABEL_KEYS (guarded by test).
_LABELS: dict[str, dict[str, str]] = {
    "en": _EN,
    "es": {
        "date": "Fecha",
        "domain": "Dominio",
        "taxonomy": "Taxonomía",
        "filter": "Filtro",
        "active_comments": "Comentarios activos",
        "overall_feedback": "Valoración general",
        "overall_intro": "Estas son algunas reacciones generales al documento.",
        "outline": "Resumen",
        "recommendation": "Recomendación",
        "revision_targets": "Objetivos clave de revisión",
        "status": "Estado",
        "pending": "Pendiente",
        "detailed_comments": "Comentarios detallados",
        "quote": "Cita",
        "feedback": "Comentarios",
    },
    "fr": {
        "date": "Date",
        "domain": "Domaine",
        "taxonomy": "Taxonomie",
        "filter": "Filtre",
        "active_comments": "Commentaires actifs",
        "overall_feedback": "Évaluation générale",
        "overall_intro": "Voici quelques réactions générales au document.",
        "outline": "Résumé",
        "recommendation": "Recommandation",
        "revision_targets": "Objectifs clés de révision",
        "status": "Statut",
        "pending": "En attente",
        "detailed_comments": "Commentaires détaillés",
        "quote": "Citation",
        "feedback": "Commentaire",
    },
    "de": {
        "date": "Datum",
        "domain": "Fachgebiet",
        "taxonomy": "Taxonomie",
        "filter": "Filter",
        "active_comments": "Aktive Kommentare",
        "overall_feedback": "Gesamtbewertung",
        "overall_intro": "Hier sind einige allgemeine Anmerkungen zum Dokument.",
        "outline": "Zusammenfassung",
        "recommendation": "Empfehlung",
        "revision_targets": "Zentrale Überarbeitungsziele",
        "status": "Status",
        "pending": "Ausstehend",
        "detailed_comments": "Detaillierte Kommentare",
        "quote": "Zitat",
        "feedback": "Anmerkung",
    },
    "nl": {
        "date": "Datum",
        "domain": "Vakgebied",
        "taxonomy": "Taxonomie",
        "filter": "Filter",
        "active_comments": "Actieve opmerkingen",
        "overall_feedback": "Algemene beoordeling",
        "overall_intro": "Hier zijn enkele algemene reacties op het document.",
        "outline": "Samenvatting",
        "recommendation": "Aanbeveling",
        "revision_targets": "Belangrijkste revisiedoelen",
        "status": "Status",
        "pending": "In behandeling",
        "detailed_comments": "Gedetailleerde opmerkingen",
        "quote": "Citaat",
        "feedback": "Opmerking",
    },
    "pt": {
        "date": "Data",
        "domain": "Domínio",
        "taxonomy": "Taxonomia",
        "filter": "Filtro",
        "active_comments": "Comentários ativos",
        "overall_feedback": "Avaliação geral",
        "overall_intro": "Aqui estão algumas reações gerais ao documento.",
        "outline": "Resumo",
        "recommendation": "Recomendação",
        "revision_targets": "Principais objetivos de revisão",
        "status": "Estado",
        "pending": "Pendente",
        "detailed_comments": "Comentários detalhados",
        "quote": "Citação",
        "feedback": "Comentário",
    },
    "it": {
        "date": "Data",
        "domain": "Dominio",
        "taxonomy": "Tassonomia",
        "filter": "Filtro",
        "active_comments": "Commenti attivi",
        "overall_feedback": "Valutazione complessiva",
        "overall_intro": "Ecco alcune reazioni generali al documento.",
        "outline": "Sintesi",
        "recommendation": "Raccomandazione",
        "revision_targets": "Obiettivi chiave di revisione",
        "status": "Stato",
        "pending": "In sospeso",
        "detailed_comments": "Commenti dettagliati",
        "quote": "Citazione",
        "feedback": "Commento",
    },
    "zh-Hans": {
        "date": "日期",
        "domain": "领域",
        "taxonomy": "分类",
        "filter": "筛选",
        "active_comments": "活动评论",
        "overall_feedback": "总体评价",
        "overall_intro": "以下是对该文档的一些总体反馈。",
        "outline": "概要",
        "recommendation": "建议",
        "revision_targets": "主要修改目标",
        "status": "状态",
        "pending": "待处理",
        "detailed_comments": "详细评论",
        "quote": "引文",
        "feedback": "反馈",
    },
    "zh-Hant": {
        "date": "日期",
        "domain": "領域",
        "taxonomy": "分類",
        "filter": "篩選",
        "active_comments": "使用中的評論",
        "overall_feedback": "總體評價",
        "overall_intro": "以下是對該文件的一些總體回饋。",
        "outline": "概要",
        "recommendation": "建議",
        "revision_targets": "主要修改目標",
        "status": "狀態",
        "pending": "待處理",
        "detailed_comments": "詳細評論",
        "quote": "引文",
        "feedback": "回饋",
    },
    "ja": {
        "date": "日付",
        "domain": "分野",
        "taxonomy": "分類",
        "filter": "フィルター",
        "active_comments": "アクティブなコメント",
        "overall_feedback": "総合評価",
        "overall_intro": "本文書に対する全体的な所見は以下のとおりです。",
        "outline": "概要",
        "recommendation": "推奨",
        "revision_targets": "主要な改訂目標",
        "status": "ステータス",
        "pending": "保留中",
        "detailed_comments": "詳細なコメント",
        "quote": "引用",
        "feedback": "フィードバック",
    },
    "ko": {
        "date": "날짜",
        "domain": "분야",
        "taxonomy": "분류",
        "filter": "필터",
        "active_comments": "활성 코멘트",
        "overall_feedback": "종합 평가",
        "overall_intro": "다음은 이 문서에 대한 전반적인 의견입니다.",
        "outline": "개요",
        "recommendation": "권고",
        "revision_targets": "주요 수정 목표",
        "status": "상태",
        "pending": "대기 중",
        "detailed_comments": "상세 코멘트",
        "quote": "인용",
        "feedback": "피드백",
    },
    "ar": {
        "date": "التاريخ",
        "domain": "المجال",
        "taxonomy": "التصنيف",
        "filter": "التصفية",
        "active_comments": "التعليقات النشطة",
        "overall_feedback": "التقييم العام",
        "overall_intro": "فيما يلي بعض الملاحظات العامة على المستند.",
        "outline": "ملخص",
        "recommendation": "التوصية",
        "revision_targets": "أهداف المراجعة الرئيسية",
        "status": "الحالة",
        "pending": "قيد الانتظار",
        "detailed_comments": "تعليقات مفصلة",
        "quote": "اقتباس",
        "feedback": "ملاحظة",
    },
}


def review_labels(language_code: str | None) -> dict[str, str]:
    """Return the label dict for a language code, English for unknown/empty.

    The returned dict always defines every key in ``_LABEL_KEYS`` (missing
    per-language keys fall back to their English value), so callers can index it
    unconditionally.
    """
    overrides = _LABELS.get((language_code or "").strip(), {})
    if not overrides:
        return _EN
    return {**_EN, **overrides}


# ---------------------------------------------------------------------------
# Completion-email copy (worker → user), localized to the review language.
# Distinct from the review labels above; the brand signature "— coarse" is
# intentionally left untranslated. English values are byte-identical to the
# previous hardcoded copy so an English review's email is unchanged.
# ---------------------------------------------------------------------------
_EMAIL_KEYS = ("subject", "ready", "view", "key_label", "key_hint")

_EMAIL_EN: dict[str, str] = {
    "subject": "Your paper review is ready",
    "ready": "Your review is ready.",
    "view": "View your review →",
    "key_label": "Review key:",
    "key_hint": "Save this key to return to your review later.",
}

_EMAIL: dict[str, dict[str, str]] = {
    "en": _EMAIL_EN,
    "es": {
        "subject": "La revisión de tu artículo está lista",
        "ready": "Tu revisión está lista.",
        "view": "Ver tu revisión →",
        "key_label": "Clave de la revisión:",
        "key_hint": "Guarda esta clave para volver a tu revisión más tarde.",
    },
    "fr": {
        "subject": "L'évaluation de votre article est prête",
        "ready": "Votre évaluation est prête.",
        "view": "Voir votre évaluation →",
        "key_label": "Clé de l'évaluation :",
        "key_hint": "Conservez cette clé pour revenir à votre évaluation plus tard.",
    },
    "de": {
        "subject": "Die Begutachtung Ihres Papiers ist fertig",
        "ready": "Ihre Begutachtung ist fertig.",
        "view": "Begutachtung ansehen →",
        "key_label": "Begutachtungsschlüssel:",
        "key_hint": "Bewahren Sie diesen Schlüssel auf, um später zur Begutachtung zurückzukehren.",
    },
    "nl": {
        "subject": "De beoordeling van je artikel is klaar",
        "ready": "Je beoordeling is klaar.",
        "view": "Bekijk je beoordeling →",
        "key_label": "Beoordelingssleutel:",
        "key_hint": "Bewaar deze sleutel om later terug te keren naar je beoordeling.",
    },
    "pt": {
        "subject": "A revisão do seu artigo está pronta",
        "ready": "Sua revisão está pronta.",
        "view": "Ver sua revisão →",
        "key_label": "Chave da revisão:",
        "key_hint": "Guarde esta chave para voltar à sua revisão mais tarde.",
    },
    "it": {
        "subject": "La revisione del tuo articolo è pronta",
        "ready": "La tua revisione è pronta.",
        "view": "Vedi la tua revisione →",
        "key_label": "Chiave della revisione:",
        "key_hint": "Conserva questa chiave per tornare alla tua revisione più tardi.",
    },
    "zh-Hans": {
        "subject": "您的论文评审已完成",
        "ready": "您的评审已完成。",
        "view": "查看您的评审 →",
        "key_label": "评审密钥：",
        "key_hint": "请保存此密钥，以便日后返回查看您的评审。",
    },
    "zh-Hant": {
        "subject": "您的論文評審已完成",
        "ready": "您的評審已完成。",
        "view": "檢視您的評審 →",
        "key_label": "評審金鑰：",
        "key_hint": "請保存此金鑰，以便日後返回查看您的評審。",
    },
    "ja": {
        "subject": "論文のレビューが完成しました",
        "ready": "レビューが完成しました。",
        "view": "レビューを見る →",
        "key_label": "レビューキー：",
        "key_hint": "後でレビューに戻れるよう、このキーを保存してください。",
    },
    "ko": {
        "subject": "논문 리뷰가 완료되었습니다",
        "ready": "리뷰가 완료되었습니다.",
        "view": "리뷰 보기 →",
        "key_label": "리뷰 키:",
        "key_hint": "나중에 리뷰로 돌아올 수 있도록 이 키를 저장하세요.",
    },
    "ar": {
        "subject": "اكتملت مراجعة بحثك",
        "ready": "اكتملت مراجعتك.",
        "view": "عرض مراجعتك ←",
        "key_label": "مفتاح المراجعة:",
        "key_hint": "احتفظ بهذا المفتاح للعودة إلى مراجعتك لاحقًا.",
    },
}


def email_completion_labels(language_code: str | None) -> dict[str, str]:
    """Return localized completion-email copy, English for unknown/empty."""
    overrides = _EMAIL.get((language_code or "").strip(), {})
    if not overrides:
        return _EMAIL_EN
    return {**_EMAIL_EN, **overrides}
