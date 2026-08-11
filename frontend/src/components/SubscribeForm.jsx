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
        <p className="text-brand-200">
          You're subscribed! Check your inbox for confirmation.
        </p>
      </>
    );
  }

  return (
    <>
      <h2 className="font-serif text-2xl font-bold text-brand-50">
        Get daily AI news in your inbox
      </h2>
      <p className="mt-1 text-brand-300">
        Choose your sections and we'll send you a daily digest.
      </p>

      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-4">
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="w-full rounded-md border border-brand-600 bg-brand-900 px-4 py-2 text-brand-50 placeholder:text-brand-500"
        />

        <div className="flex flex-wrap gap-4">
          {SECTIONS.map((section) => (
            <label key={section.key} className="flex items-center gap-2 text-sm text-brand-200">
              <input
                type="checkbox"
                checked={selectedSections.includes(section.key)}
                onChange={() => toggleSection(section.key)}
              />
              {section.label}
            </label>
          ))}
        </div>

        {errorMessage && <p className="text-sm text-red-400">{errorMessage}</p>}

        <button
          type="submit"
          disabled={status === 'submitting' || selectedSections.length === 0}
          className="rounded-md bg-accent-500 px-6 py-2 text-brand-900 hover:bg-accent-600 disabled:opacity-50"
        >
          {status === 'submitting' ? 'Subscribing...' : 'Subscribe'}
        </button>
      </form>
    </>
  );
}
