type PlanSectionProps = {
  id: string;
  title: string;
  description?: string;
  children: React.ReactNode;
};

export function PlanSection({ id, title, description, children }: PlanSectionProps) {
  return (
    <section id={id} className="scroll-mt-24">
      <div className="mb-4 border-b border-zinc-200 pb-3 dark:border-zinc-800">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
          {title}
        </h2>
        {description ? (
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            {description}
          </p>
        ) : null}
      </div>
      {children}
    </section>
  );
}
