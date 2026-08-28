import { notFound } from "next/navigation";

import { ChatWorkspace } from "@/components/chat-workspace";
import { EvaluationWorkspace } from "@/components/evaluation-workspace";
import { FoundationState } from "@/components/foundation-state";
import { AiLabWorkspace } from "@/components/ai-lab-workspace";
import { KnowledgeBaseWorkspace } from "@/components/knowledge-base-workspace";
import { findSection, sections } from "@/lib/sections";

export function generateStaticParams() {
  return sections.map(({ slug }) => ({ section: slug }));
}

export default async function SectionPage({ params }: Readonly<{ params: Promise<{ section: string }> }>) {
  const { section: slug } = await params;
  const section = findSection(slug);
  if (!section) notFound();
  if (slug === "chat") return <ChatWorkspace />;
  if (slug === "knowledge-base") return <KnowledgeBaseWorkspace />;
  if (slug === "ai-lab") return <AiLabWorkspace />;
  if (slug === "evaluation") return <EvaluationWorkspace />;
  return <FoundationState section={section} />;
}
