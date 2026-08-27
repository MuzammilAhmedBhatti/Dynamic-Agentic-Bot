export const sections = [
  { slug: "chat", label: "Chat", phase: "Phase 7", description: "Grounded conversations and evidence." },
  { slug: "knowledge-base", label: "Knowledge Base", phase: "Phase 2", description: "Documents, datasets, and ingestion status." },
  { slug: "agents", label: "Agents", phase: "Phase 4", description: "Personas, routing, and tool policies." },
  { slug: "ai-lab", label: "AI Lab", phase: "Phases 8–9", description: "Isolated curriculum experiments." },
  { slug: "evaluation", label: "Evaluation", phase: "Phase 10", description: "Quality, grounding, routing, and safety metrics." },
  { slug: "security", label: "Security", phase: "Phase 11", description: "Audit, policy, and security posture." },
  { slug: "admin", label: "Admin", phase: "Phase 7", description: "Tenant, model, prompt, and provider administration." }
] as const;

export type Section = (typeof sections)[number];

export function findSection(slug: string): Section | undefined {
  return sections.find((section) => section.slug === slug);
}
