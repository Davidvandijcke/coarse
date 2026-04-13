import type { Metadata } from "next";
import ReviewPageClient from "./ReviewPageClient";

type Props = {
  params: Promise<{ id: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const fallbackTitle = "\u2018coarse \u2014 AI Paper Review";
  const description =
    "Check out my paper\u2019s AI review by \u2018coarse, the free and open-source AI peer reviewer.";

  return {
    title: fallbackTitle,
    description,
    openGraph: {
      title: fallbackTitle,
      description,
      type: "article",
      siteName: "\u2018coarse",
    },
    twitter: {
      card: "summary",
      title: fallbackTitle,
      description,
    },
  };
}

export default async function ReviewPage({ params }: Props) {
  const { id } = await params;
  return <ReviewPageClient id={id} />;
}
