import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useArticles } from '../hooks/useArticles';
import { getSourceLogoUrl } from '../utils/sourceLogos';

// Full blog-post-style page for a single article, reached via /article/:id.
// Reuses useArticles() (same hook HomePage uses) rather than a dedicated
// backend endpoint, then finds the matching article client-side — simple
// and sufficient given the current data volume.
export default function ArticlePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data, loading, error } = useArticles();
  const [imageFailed, setImageFailed] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-brand-900 p-8 text-center text-brand-300">
        Loading...
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

  const allArticles = Object.values(data).flat();
  const article = allArticles.find((a) => a.id === id);

  if (!article) {
    return (
      <div className="min-h-screen bg-brand-900 p-8 text-center">
        <p className="mb-4 text-brand-300">Article not found.</p>
        <Link
          to="/"
          className="font-medium text-accent-400 hover:text-accent-500"
        >
          ← Back to all articles
        </Link>
      </div>
    );
  }

  const {
    title,
    hook,
    source_name,
    published_at,
    summary_paragraph,
    key_points,
    source_url,
    image_url,
  } = article;

  const formattedDate = published_at
    ? new Date(published_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : source_name === 'GitHub Trending'
      ? 'Trending'
      : 'Recently added';

  const sourceLogoUrl = getSourceLogoUrl(source_name);
  const displayImageUrl = image_url || sourceLogoUrl;
  const showImage = displayImageUrl && !imageFailed;
  const isFallbackLogo = showImage && !image_url;

  return (
    <div className="min-h-screen bg-brand-900 p-8 md:p-12">
      <div className="mx-auto max-w-4xl">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="mb-8 text-sm font-medium text-accent-400 hover:text-accent-500"
        >
          ← Back
        </button>

        <h1 className="font-serif text-4xl font-bold text-brand-50 md:text-5xl">{title}</h1>
        <p className="mt-4 text-lg text-brand-300">{hook}</p>

        <div className="mt-6 flex items-center gap-3 text-sm text-brand-400">
          {sourceLogoUrl && (
            <img
              src={sourceLogoUrl}
              alt=""
              className="h-6 w-6 rounded-full object-contain"
            />
          )}
          <span>{source_name}</span>
          <span>·</span>
          <span>{formattedDate}</span>
        </div>

        {summary_paragraph && (
          <p className="mt-6 text-lg leading-relaxed text-brand-200">{summary_paragraph}</p>
        )}

        {showImage &&
          (isFallbackLogo ? (
            <div className="mt-8 flex h-96 w-full items-center justify-center rounded-lg border border-brand-700 bg-white">
              <img
                src={displayImageUrl}
                alt=""
                className="h-32 w-32 object-contain"
                onError={() => setImageFailed(true)}
              />
            </div>
          ) : (
            <img
              src={displayImageUrl}
              alt=""
              className="mt-8 h-96 w-full rounded-lg object-cover"
              onError={() => setImageFailed(true)}
            />
          ))}

        <div className="mx-auto mt-10 max-w-3xl">
          <h2 className="font-serif text-xl font-semibold text-brand-50">Key Points</h2>
          <div className="mt-4">
            {key_points.map((point, index) => (
              <p key={index} className="mt-4 text-lg leading-relaxed text-brand-200 first:mt-0">
                {point}
              </p>
            ))}
          </div>

          <a
            href={source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-10 inline-flex items-center gap-2 text-lg font-medium text-accent-400 hover:text-accent-500"
          >
            Read full article
            <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>
    </div>
  );
}
