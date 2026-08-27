import { notFound } from "next/navigation";

import { FoundationState } from "@/components/foundation-state";
import { findSection, sections } from "@/lib/sections";

export function generateStaticParams() {
  return sections.map(({ slug }) => ({ section: slug }));
}

export default async function SectionPage({ params }: Readonly<{ params: Promise<{ section: string }> }>) {
  const { section: slug } = await params;
  const section = findSection(slug);
  if (!section) notFound();
  return <FoundationState section={section} />;
}
