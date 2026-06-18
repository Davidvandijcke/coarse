/**
 * Parse a coarse review markdown string into structured data.
 *
 * Expected format matches synthesis.py output:
 *   # Title
 *   **Date**: ... / **Domain**: ... / **Taxonomy**: ...
 *   ## Overall Feedback
 *   **Issue Title** \n body ...
 *   ## Detailed Comments (N)
 *   ### 1. Comment Title
 *   **Quote**: \n > ... \n **Feedback**: \n ...
 *
 * The section/field labels above are localized: a review rendered in another
 * language uses translated anchors (e.g. "## Valoración general"). This parser
 * is the legacy/fallback path — localized reviews normally render from
 * result_json — but it must still parse a localized review that lacks
 * result_json. Pass the review's language code so the anchors match; omitting it
 * (or passing empty) yields English, identical to the original behavior.
 */

import { reviewLabels } from "./reviewLabels";

/** Escape regex metacharacters so a label can be safely interpolated into RegExp. */
function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export interface OverallIssue {
  title: string;
  body: string;
}

export interface DetailedComment {
  number: number;
  title: string;
  status: string;
  quote: string;
  feedback: string;
}

export interface ParsedReview {
  title: string;
  metadata: { date: string; domain: string; taxonomy: string };
  overallFeedback: {
    summary: string | null;
    issues: OverallIssue[];
  };
  detailedComments: DetailedComment[];
}

function extractMeta(text: string, key: string): string {
  const re = new RegExp(`\\*\\*${escapeRegExp(key)}\\*\\*:\\s*(.+)`);
  return re.exec(text)?.[1]?.trim() ?? "";
}

function parseOverallSection(
  text: string,
  L: ReturnType<typeof reviewLabels>
): ParsedReview["overallFeedback"] {
  // Remove the intro line ("Here are some overall reactions...") in its language.
  const cleaned = text.replace(
    new RegExp("^" + escapeRegExp(L.overall_intro) + "[^\\n]*\\n*", "i"),
    ""
  );

  // Split on bold titles: **Title**\n
  // But exclude **Status**: and **Outline**
  const parts = cleaned.split(new RegExp("\\n\\*\\*(?!" + escapeRegExp(L.status) + ")"));

  let summary: string | null = null;
  const issues: OverallIssue[] = [];

  for (const part of parts) {
    if (!part.trim()) continue;

    // Each part starts with "Title**\nBody..." (we split after the first **)
    const match = part.match(/^(.+?)\*\*\s*\n([\s\S]*)/);
    if (!match) continue;

    const title = match[1].trim();
    const body = match[2].trim();

    if (title === L.outline) {
      summary = body;
    } else if (title.startsWith(L.status)) {
      // Skip the status line
      continue;
    } else {
      issues.push({ title, body });
    }
  }

  return { summary, issues };
}

function parseDetailedComments(
  text: string,
  L: ReturnType<typeof reviewLabels>
): DetailedComment[] {
  const status = escapeRegExp(L.status);
  const quoteLabel = escapeRegExp(L.quote);
  const feedbackLabel = escapeRegExp(L.feedback);

  // Split on ### N. Title headers (structural, not language-dependent)
  const sections = text.split(/(?=^### \d+\.\s)/m).filter((s) => s.trim());
  const comments: DetailedComment[] = [];

  for (const section of sections) {
    const headerMatch = section.match(/^### (\d+)\.\s+(.+)/);
    if (!headerMatch) continue;

    const number = parseInt(headerMatch[1], 10);
    const title = headerMatch[2].trim();

    // Extract status
    const statusMatch = section.match(
      new RegExp("\\*\\*" + status + "\\*\\*:\\s*\\[?([^\\]\\n]+)\\]?")
    );
    const statusValue = statusMatch?.[1]?.trim() ?? L.pending;

    // Extract quote: everything between **Quote**: and **Feedback**:
    const quoteMatch = section.match(
      new RegExp(
        "\\*\\*" + quoteLabel + "\\*\\*:\\s*\\n([\\s\\S]*?)(?=\\n\\*\\*" + feedbackLabel + "\\*\\*:)"
      )
    );
    let quote = "";
    if (quoteMatch) {
      // Strip leading "> " from each line
      quote = quoteMatch[1]
        .split("\n")
        .map((line) => line.replace(/^>\s?/, ""))
        .join("\n")
        .trim();
    }

    // Extract feedback: everything after **Feedback**:\n
    const feedbackMatch = section.match(
      new RegExp("\\*\\*" + feedbackLabel + "\\*\\*:\\s*\\n([\\s\\S]*?)(?=\\n---|\\n### |\\s*$)")
    );
    const feedback = feedbackMatch?.[1]?.trim() ?? "";

    comments.push({ number, title, status: statusValue, quote, feedback });
  }

  return comments;
}

export function parseReview(
  markdown: string,
  languageCode?: string | null
): ParsedReview | null {
  if (!markdown) return null;

  // Localized labels for this review's language (English for unknown/empty).
  const L = reviewLabels(languageCode);

  // Extract title from first # heading
  const titleMatch = markdown.match(/^# (.+)/m);
  const title = titleMatch?.[1]?.trim() ?? "";

  // Extract metadata
  const metadata = {
    date: extractMeta(markdown, L.date),
    domain: extractMeta(markdown, L.domain),
    taxonomy: extractMeta(markdown, L.taxonomy),
  };

  // Split into major sections
  const overallHeading = "## " + L.overall_feedback;
  const overallStart = markdown.indexOf(overallHeading);
  const detailedStart = markdown.search(new RegExp("## " + escapeRegExp(L.detailed_comments)));

  if (overallStart === -1 || detailedStart === -1) return null;

  const overallText = markdown.slice(overallStart + overallHeading.length, detailedStart);
  const detailedText = markdown.slice(
    detailedStart + markdown.slice(detailedStart).indexOf("\n") + 1
  );

  return {
    title,
    metadata,
    overallFeedback: parseOverallSection(overallText, L),
    detailedComments: parseDetailedComments(detailedText, L),
  };
}
