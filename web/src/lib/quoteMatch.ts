/**
 * Find the block index in the paper markdown that best matches a quote.
 *
 * Splits paper by double-newline into blocks, then searches with
 * increasingly loose strategies until a match is found.
 */

function normalize(s: string): string {
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}

/** Strip markdown formatting chars for text-level comparison. */
function stripMarkdown(s: string): string {
  return s
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/\*(.+?)\*/g, "$1")
    .replace(/_(.+?)_/g, "$1")
    .replace(/`(.+?)`/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/^#+\s*/gm, "")
    .replace(/^>\s*/gm, "");
}

export function splitIntoBlocks(markdown: string): string[] {
  return markdown.split(/\n{2,}/).filter((b) => b.trim().length > 0);
}

export function findQuoteInBlocks(
  quote: string,
  blocks: string[]
): number | null {
  const normQuote = normalize(stripMarkdown(quote));
  if (normQuote.length < 10) return null;

  // Pass 1: exact substring in a single block
  for (let i = 0; i < blocks.length; i++) {
    const blockNorm = normalize(stripMarkdown(blocks[i]));
    if (blockNorm.includes(normQuote)) return i;
  }

  // Pass 2: substring across 2-3 consecutive blocks
  for (let i = 0; i < blocks.length - 1; i++) {
    const joined = normalize(
      stripMarkdown(
        blocks
          .slice(i, Math.min(i + 3, blocks.length))
          .join(" ")
      )
    );
    if (joined.includes(normQuote)) return i;
  }

  // Pass 3: first 60 chars prefix match
  const prefix = normQuote.slice(0, 60);
  if (prefix.length >= 20) {
    for (let i = 0; i < blocks.length; i++) {
      const blockNorm = normalize(stripMarkdown(blocks[i]));
      if (blockNorm.includes(prefix)) return i;
    }
  }

  // Pass 4: last 60 chars suffix match
  const suffix = normQuote.slice(-60);
  if (suffix.length >= 20) {
    for (let i = 0; i < blocks.length; i++) {
      const blockNorm = normalize(stripMarkdown(blocks[i]));
      if (blockNorm.includes(suffix)) return i;
    }
  }

  return null;
}
