/**
 * Convert LaTeX-style math delimiters to $/$$ style for remark-math compatibility.
 *
 * remark-math only handles $...$ (inline) and $$...$$ (display).
 * Academic papers extracted from PDF often use \[...\], \(...\),
 * and bare \begin{equation} etc.
 */
export function preprocessLatex(text: string): string {
  // \[...\] → display math (possibly multiline)
  text = text.replace(
    /\\\[([\s\S]*?)\\\]/g,
    (_m, inner: string) => `\n$$\n${inner.trim()}\n$$\n`,
  );

  // \(...\) → inline math
  text = text.replace(
    /\\\(([\s\S]*?)\\\)/g,
    (_m, inner: string) => `$${inner}$`,
  );

  // Wrap standalone math environments not already inside $ or $$
  const envNames = [
    "equation",
    "equation\\*",
    "align",
    "align\\*",
    "aligned",
    "gather",
    "gather\\*",
    "multline",
    "multline\\*",
    "split",
    "cases",
    "array",
    "matrix",
    "pmatrix",
    "bmatrix",
    "vmatrix",
    "Vmatrix",
    "eqnarray",
    "eqnarray\\*",
  ].join("|");

  const envRegex = new RegExp(
    `(?<!\\$)(\\\\begin\\{(?:${envNames})\\}[\\s\\S]*?\\\\end\\{(?:${envNames})\\})(?!\\$)`,
    "g",
  );
  text = text.replace(envRegex, (_m, inner: string) => `\n$$\n${inner}\n$$\n`);

  return text;
}
