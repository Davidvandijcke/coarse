import { Resend } from "resend";

const FROM_ADDRESS = "coarse <reviews@coarse.ink>";

/**
 * Best-effort transactional email send via Resend. Never throws.
 *
 * The Gmail outage that this replaces was caused by an uncaught
 * `await mailer.sendMail(...)` rejecting out of the /api/submit route,
 * producing an empty 500 that the browser surfaced as "Unexpected end
 * of JSON input" on every submission. This wrapper MUST stay best-effort
 * forever: callers do not need to wrap it in try/catch, and any future
 * refactor that makes it throw is a regression.
 */
export async function sendReviewEmail(args: {
  to: string;
  subject: string;
  html: string;
  reviewId?: string;
}): Promise<void> {
  const apiKey = process.env.RESEND_API_KEY?.trim();
  const logPrefix = args.reviewId ? `[${args.reviewId}] ` : "";
  if (!apiKey) {
    console.error(`${logPrefix}RESEND_API_KEY missing; dropping send to ${args.to}`);
    return;
  }

  try {
    const resend = new Resend(apiKey);
    const { data, error } = await resend.emails.send({
      from: FROM_ADDRESS,
      to: args.to,
      subject: args.subject,
      html: args.html,
      ...(args.reviewId
        ? { tags: [{ name: "review_id", value: args.reviewId }] }
        : {}),
    });
    if (error || !data?.id) {
      console.error(
        `${logPrefix}Resend send failed: ${error?.message ?? "no id returned"}`,
      );
      return;
    }
    console.log(`${logPrefix}Resend send ok id=${data.id} to=${args.to}`);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`${logPrefix}Resend send threw: ${message}`);
  }
}
