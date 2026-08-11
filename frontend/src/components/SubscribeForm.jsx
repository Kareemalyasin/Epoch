import { useState } from 'react';

const SECTIONS = [
  { key: 'new_models', label: 'New Models' },
  { key: 'open_source', label: 'Open Source' },
  { key: 'ai_tools', label: 'AI Tools' },
  { key: 'claude_ecosystem', label: 'Claude' },
];

// Lets a visitor subscribe to a daily digest for one or more sections.
// Posts to the backend's /subscribers/ signup endpoint and shows a success
// message in place of the form once subscribed.
export default function SubscribeForm() {
  const [email, setEmail] = useState('');
  const [selectedSections, setSelectedSections] = useState([
    'new_models',
    'open_source',
    'ai_tools',
    'claude_ecosystem',
  ]);
  const [status, setStatus] = useState('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const toggleSection = (key) => {
    setSelectedSections((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('submitting');
    setErrorMessage('');

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/subscribers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, subscribed_sections: selectedSections }),
      });

      if (response.ok) {
        setStatus('success');
        return;
      }

      if (response.status === 409) {
        setErrorMessage('This email is already subscribed.');
      } else {
        setErrorMessage('Something went wrong. Please try again.');
      }
      setStatus('idle');
    } catch {
      setErrorMessage('Something went wrong. Please try again.');
      setStatus('idle');
    }
  };

  if (status === 'success') {
    return (
      <>
        <p className="relative z-10 text-brand-200">
          You're subscribed! Check your inbox for confirmation.
        </p>
      </>
    );
  }

  return (
    <>
      <div className="relative z-10 mb-3 inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-accent-400">
        <span className="h-1.5 w-1.5 rounded-full bg-accent-500" />
        Daily digest
      </div>

      <h2 className="relative z-10 max-w-xs font-serif text-2xl font-bold leading-tight text-brand-50">
        Get the day's AI news in one email.
      </h2>
      <p className="relative z-10 mt-2 text-sm leading-relaxed text-brand-300">
        Pick what matters to you. We'll send a single digest, once a day, only for the sections you choose.
      </p>

      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-4">
        <div>
          <label className="relative z-10 mt-6 block text-xs font-semibold uppercase tracking-wide text-brand-500">
            Email address
          </label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="relative z-10 mt-2 w-full rounded-lg border border-brand-600 bg-brand-900 px-4 py-3 text-sm text-brand-50 placeholder:text-brand-600 outline-none focus:border-accent-500"
          />
        </div>

        <div>
          <label className="relative z-10 mt-5 block text-xs font-semibold uppercase tracking-wide text-brand-500">
            Sections
          </label>
          <div className="relative z-10 mt-2 grid grid-cols-2 gap-2">
            {SECTIONS.map((section) => {
              const isSelected = selectedSections.includes(section.key);
              return (
                <button
                  key={section.key}
                  type="button"
                  onClick={() => toggleSection(section.key)}
                  className={`flex items-center gap-2 rounded-lg border px-3 py-2.5 text-sm font-medium transition-colors ${
                    isSelected
                      ? 'border-accent-500 bg-accent-500/10 text-brand-50'
                      : 'border-brand-600 bg-brand-900 text-brand-300'
                  }`}
                >
                  <span
                    className={`flex h-4 w-4 items-center justify-center rounded ${
                      isSelected ? 'bg-accent-500' : 'border border-brand-600'
                    }`}
                  >
                    {isSelected && <span className="text-[10px] font-bold text-brand-900">✓</span>}
                  </span>
                  {section.label}
                </button>
              );
            })}
          </div>
        </div>

        {errorMessage && <p className="relative z-10 text-sm text-red-400">{errorMessage}</p>}

        <button
          type="submit"
          disabled={status === 'submitting' || selectedSections.length === 0}
          className="relative z-10 mt-6 w-full rounded-md bg-accent-500 px-6 py-2 text-brand-900 hover:bg-accent-600 disabled:opacity-50"
        >
          {status === 'submitting' ? 'Subscribing...' : 'Subscribe'}
        </button>

        <p className="relative z-10 mt-3 text-center text-xs text-brand-500">
          One email a day. Unsubscribe anytime with one click.
        </p>
      </form>
    </>
  );
}
