import { papers } from "@/data/compare";
import { ComparePage } from "@/components/ComparePage";

export const metadata = {
  title: "\u2018coarse \u2014 Compare reviews",
  description: "See how coarse stacks up against refine.ink and human reviewers.",
};

export default function CompareRoute() {
  // Serialize papers data for client component (JSON-safe)
  const serialized = JSON.parse(JSON.stringify(papers));
  return <ComparePage papers={serialized} />;
}
