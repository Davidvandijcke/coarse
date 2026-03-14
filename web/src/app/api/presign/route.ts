import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import { checkRateLimit } from "@/lib/rateLimit";

const SUPPORTED_EXTENSIONS = new Set([
  ".pdf", ".txt", ".md", ".tex", ".latex",
  ".html", ".htm", ".docx", ".epub",
]);

function getExtension(filename: string): string {
  const dot = filename.lastIndexOf(".");
  return dot >= 0 ? filename.slice(dot).toLowerCase() : "";
}

export async function POST(request: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json(
      { error: "Server not configured" },
      { status: 503 }
    );
  }

  const supabaseAdmin = createClient(supabaseUrl, supabaseKey);

  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  const rateLimited = await checkRateLimit(supabaseAdmin, ip, "presign");
  if (rateLimited) return rateLimited;

  let filename = "";
  try {
    const body = await request.json();
    filename = (body.filename ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!filename) {
    return NextResponse.json({ error: "No filename provided" }, { status: 400 });
  }

  if (filename.length > 255) {
    return NextResponse.json({ error: "Filename too long" }, { status: 400 });
  }

  const ext = getExtension(filename);
  if (!SUPPORTED_EXTENSIONS.has(ext)) {
    return NextResponse.json(
      { error: `Unsupported format. Supported: ${[...SUPPORTED_EXTENSIONS].join(", ")}` },
      { status: 400 },
    );
  }

  // Create review record to get UUID
  const { data: reviewRow, error: insertError } = await supabaseAdmin
    .from("reviews")
    .insert({ paper_filename: filename, status: "queued" })
    .select("id")
    .single();

  if (insertError || !reviewRow) {
    return NextResponse.json({ error: "Failed to create review record" }, { status: 500 });
  }

  const id: string = reviewRow.id;
  const storagePath = `${id}${ext}`;

  // Create a signed upload URL for direct client upload
  const { data: uploadData, error: uploadError } = await supabaseAdmin.storage
    .from("papers")
    .createSignedUploadUrl(storagePath);

  if (uploadError || !uploadData) {
    await supabaseAdmin.from("reviews").delete().eq("id", id);
    return NextResponse.json({ error: "Failed to create upload URL" }, { status: 500 });
  }

  return NextResponse.json({
    id,
    storagePath,
    signedUrl: uploadData.signedUrl,
    token: uploadData.token,
  });
}
