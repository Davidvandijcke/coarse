import type { Metadata } from "next";
import { createClient } from "@supabase/supabase-js";
import ReviewPageClient from "./ReviewPageClient";

type Props = {
  params: Promise<{ id: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  const fallbackTitle = "\u2018coarse \u2014 AI Paper Review";
  const description =
    "Check out my paper\u2019s AI review by \u2018coarse, the free and open-source AI peer reviewer.";

  if (!supabaseUrl || !supabaseKey) {
    return { title: fallbackTitle, description };
  }

  const supabase = createClient(supabaseUrl, supabaseKey);
  const { data } = await supabase
    .from("reviews")
    .select("paper_title")
    .eq("id", id)
    .single();

  const title = data?.paper_title
    ? `Review of \u201c${data.paper_title}\u201d`
    : fallbackTitle;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      type: "article",
      siteName: "\u2018coarse",
    },
    twitter: {
      card: "summary",
      title,
      description,
    },
  };
}

export default async function ReviewPage({ params }: Props) {
  const { id } = await params;
  return <ReviewPageClient id={id} />;
}
