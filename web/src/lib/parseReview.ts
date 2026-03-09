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
 */

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
  const re = new RegExp(`\\*\\*${key}\\*\\*:\\s*(.+)`);
  return re.exec(text)?.[1]?.trim() ?? "";
}

function parseOverallSection(text: string): ParsedReview["overallFeedback"] {
  // Remove the intro line "Here are some overall reactions..."
  const cleaned = text.replace(/^Here are some overall reactions[^\n]*\n*/i, "");

  // Split on bold titles: **Title**\n
  // But exclude **Status**: and **Outline**
  const parts = cleaned.split(/\n\*\*(?!Status)/);

  let summary: string | null = null;
  const issues: OverallIssue[] = [];

  for (const part of parts) {
    if (!part.trim()) continue;

    // Each part starts with "Title**\nBody..." (we split after the first **)
    const match = part.match(/^(.+?)\*\*\s*\n([\s\S]*)/);
    if (!match) continue;

    const title = match[1].trim();
    const body = match[2].trim();

    if (title === "Outline") {
      summary = body;
    } else if (title.startsWith("Status")) {
      // Skip the status line
      continue;
    } else {
      issues.push({ title, body });
    }
  }

  return { summary, issues };
}

function parseDetailedComments(text: string): DetailedComment[] {
  // Split on ### N. Title headers
  const sections = text.split(/(?=^### \d+\.\s)/m).filter((s) => s.trim());
  const comments: DetailedComment[] = [];

  for (const section of sections) {
    const headerMatch = section.match(/^### (\d+)\.\s+(.+)/);
    if (!headerMatch) continue;

    const number = parseInt(headerMatch[1], 10);
    const title = headerMatch[2].trim();

    // Extract status
    const statusMatch = section.match(/\*\*Status\*\*:\s*\[?([^\]\n]+)\]?/);
    const status = statusMatch?.[1]?.trim() ?? "Pending";

    // Extract quote: everything between **Quote**: and **Feedback**:
    const quoteMatch = section.match(
      /\*\*Quote\*\*:\s*\n([\s\S]*?)(?=\n\*\*Feedback\*\*:)/
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
    const feedbackMatch = section.match(/\*\*Feedback\*\*:\s*\n([\s\S]*?)(?=\n---|\n### |\s*$)/);
    const feedback = feedbackMatch?.[1]?.trim() ?? "";

    comments.push({ number, title, status, quote, feedback });
  }

  return comments;
}

export function parseReview(markdown: string): ParsedReview | null {
  if (!markdown) return null;

  // Extract title from first # heading
  const titleMatch = markdown.match(/^# (.+)/m);
  const title = titleMatch?.[1]?.trim() ?? "";

  // Extract metadata
  const metadata = {
    date: extractMeta(markdown, "Date"),
    domain: extractMeta(markdown, "Domain"),
    taxonomy: extractMeta(markdown, "Taxonomy"),
  };

  // Split into major sections
  const overallStart = markdown.indexOf("## Overall Feedback");
  const detailedStart = markdown.search(/## Detailed Comments/);

  if (overallStart === -1 || detailedStart === -1) return null;

  const overallText = markdown.slice(
    overallStart + "## Overall Feedback".length,
    detailedStart
  );
  const detailedText = markdown.slice(
    detailedStart + markdown.slice(detailedStart).indexOf("\n") + 1
  );

  return {
    title,
    metadata,
    overallFeedback: parseOverallSection(overallText),
    detailedComments: parseDetailedComments(detailedText),
  };
}
