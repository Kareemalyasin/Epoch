const SECTIONS = [
  { key: 'new_models', label: 'New Models' },
  { key: 'open_source', label: 'Open Source' },
  { key: 'ai_tools', label: 'AI Tools' },
  { key: 'claude_ecosystem', label: 'Claude' },
];

function hasRecentNews(articles) {
  if (!articles || articles.length === 0) return false;
  const cutoff = Date.now() - 24 * 60 * 60 * 1000;
  return articles.some((a) => new Date(a.created_at).getTime() >= cutoff);
}

// Lets the user switch between the 4 news sections. The parent component
// owns which section is "active" in state and passes it down via
// activeSection/onSectionChange. articlesBySection drives the orbit-dot
// indicator: it spins if that section has articles created in the last 24h.
export default function SectionTabs({ activeSection, onSectionChange, articlesBySection }) {
  return (
    <div className="mx-auto mb-9 flex w-fit justify-center gap-1 rounded-xl border border-brand-700 bg-brand-800 p-1.5">
      {SECTIONS.map((section) => {
        const isActive = section.key === activeSection;
        const isRecent = hasRecentNews(articlesBySection[section.key]);

        return (
          <button
            key={section.key}
            type="button"
            onClick={() => onSectionChange(section.key)}
            className={`flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-medium transition-colors ${
              isActive ? 'bg-brand-700 text-brand-50' : 'text-brand-300 hover:bg-brand-700/50'
            }`}
          >
            <span className="relative flex h-3.5 w-3.5 items-center justify-center rounded-full border border-accent-500">
              <span
                className={`absolute -top-0.5 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full bg-accent-500 ${
                  isRecent ? 'animate-spin-orbit' : 'opacity-30'
                }`}
              />
            </span>
            {section.label}
          </button>
        );
      })}
    </div>
  );
}
