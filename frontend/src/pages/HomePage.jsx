import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useArticles } from '../hooks/useArticles';
import ArticleCard from '../components/ArticleCard';
import SectionTabs from '../components/SectionTabs';
import SubscribeForm from '../components/SubscribeForm';
import EpochLogo from '../components/EpochLogo';
import { useScrollGlow } from '../hooks/useScrollGlow';
import { useSaudiClock } from '../hooks/useSaudiClock';

const SECTION_LABELS = {
  new_models: 'New Models',
  open_source: 'Open Source',
  ai_tools: 'AI Tools',
  claude_ecosystem: 'Claude',
};

// The tabbed list view: SectionTabs controls which section's articles are
// shown, ArticleCard renders each one, and clicking a card navigates to
// that article's own page (/article/:id) instead of opening a modal.
// The subscribe form is reached via a modal, triggered from the header.
function HomePage() {
  const { data, loading, error } = useArticles();
  const [activeSection, setActiveSection] = useState('new_models');
  const [showSubscribeModal, setShowSubscribeModal] = useState(false);
  const scrollProgress = useScrollGlow();
  const { date, time } = useSaudiClock();
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="min-h-screen bg-brand-900 p-8">
        <div className="mx-auto max-w-5xl">
          <div className="grid grid-cols-1 gap-7 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="overflow-hidden rounded-lg border border-brand-700 bg-brand-800">
                <div className="h-56 w-full animate-pulse bg-brand-700" />
                <div className="flex flex-col gap-3 p-6">
                  <div className="h-3 w-1/3 animate-pulse rounded bg-brand-700" />
                  <div className="h-4 w-full animate-pulse rounded bg-brand-700" />
                  <div className="h-4 w-2/3 animate-pulse rounded bg-brand-700" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-brand-900 p-8 text-center text-red-400">
        Error: {error}
      </div>
    );
  }

  const articles = data[activeSection] ?? [];
  const todayCount = articles.filter((a) => {
    const cutoff = Date.now() - 24 * 60 * 60 * 1000;
    return new Date(a.created_at).getTime() >= cutoff;
  }).length;

  return (
    <div className="min-h-screen bg-brand-900 p-8">
      <div
        className="pointer-events-none fixed inset-0 z-0"
        style={{
          background: `radial-gradient(circle at 50% 100%, rgba(217, 119, 87, ${0.05 + scrollProgress * 0.22}) 0%, rgba(217, 119, 87, 0) ${30 + scrollProgress * 45}%)`,
        }}
      />

      <div className="relative z-10 mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <EpochLogo className="h-9 w-9" />
          <h1 className="font-serif text-4xl font-bold text-brand-50">Epoch</h1>
        </div>

        <div className="hidden text-center md:block">
          <div className="font-serif text-6xl font-bold tabular-nums text-accent-500">{time}</div>
          <div className="mt-1.5 text-sm font-semibold uppercase tracking-wide text-brand-400">{date} — Riyadh</div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowSubscribeModal(true)}
            className="rounded-md bg-brand-700 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-800"
          >
            Get your favorite news →
          </button>
        </div>
      </div>

      <div className="relative z-10 mx-auto max-w-5xl">
        <div className="py-22 text-center">
          <div className="mb-7 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-accent-400">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-500 animate-pulse" />
            Updated today
          </div>
          <h2 className="mx-auto max-w-3xl font-serif text-6xl font-semibold leading-tight tracking-tight text-brand-50">
            Everything new in AI,<br />
            <span className="text-accent-500">once a day.</span>
          </h2>
          <p className="mx-auto mt-6 max-w-md text-lg text-brand-300">
            Four categories. No noise. New models, open source, tools, and Claude — read in under a minute.
          </p>
        </div>

        <SectionTabs
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          articlesBySection={data}
        />

        <div className="mb-6 pl-1 text-xs font-semibold uppercase tracking-wider text-brand-500">
          {SECTION_LABELS[activeSection]}{todayCount > 0 ? ` · ${todayCount} today` : ''}
        </div>

        {articles.length === 0 ? (
          <p className="text-brand-300">No articles in this section yet.</p>
        ) : (
          <div className="mb-10 grid grid-cols-1 gap-7 sm:grid-cols-2 lg:grid-cols-3">
            {articles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                onClick={() => navigate(`/article/${article.id}`)}
              />
            ))}
          </div>
        )}

        {showSubscribeModal && (
          <div
            onClick={() => setShowSubscribeModal(false)}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          >
            <div
              onClick={(e) => e.stopPropagation()}
              className="relative w-full max-w-md overflow-hidden rounded-2xl border border-brand-700 bg-brand-800 p-9"
            >
              <div className="pointer-events-none absolute -right-16 -top-16 h-44 w-44 rounded-full border border-accent-500/15" />
              <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full border border-accent-500/10" />

              <button
                type="button"
                onClick={() => setShowSubscribeModal(false)}
                className="absolute right-4 top-4 z-10 flex h-8 w-8 items-center justify-center rounded-full text-2xl leading-none text-brand-400 hover:text-brand-200"
                aria-label="Close"
              >
                ×
              </button>

              <SubscribeForm />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default HomePage;
