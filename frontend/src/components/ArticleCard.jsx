import { useState } from 'react';
import { getSourceLogoUrl } from '../utils/sourceLogos';

// Renders a single article summary (image, source, title, hook, date).
// Clicking it is meant to open the full detail view (key_points) via the
// onClick prop, which the parent component wires up.
export default function ArticleCard({ article, onClick }) {
  const { title, hook, source_name, published_at, image_url } = article;
  const [imageFailed, setImageFailed] = useState(false);

  const formattedDate = published_at
    ? new Date(published_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : source_name === 'GitHub Trending'
      ? 'Trending'
      : 'Recently added';

  const displayImageUrl = image_url || getSourceLogoUrl(source_name);
  const showImage = displayImageUrl && !imageFailed;
  const isFallbackLogo = showImage && !image_url;

  return (
    <div
      onClick={onClick}
      className="min-h-[300px] cursor-pointer overflow-hidden rounded-lg border border-brand-700 bg-brand-800 transition-colors hover:border-brand-500"
    >
      {showImage &&
        (isFallbackLogo ? (
          <div className="flex h-56 w-full items-center justify-center rounded-t-lg border-b border-brand-700 bg-white">
            <img
              src={displayImageUrl}
              alt=""
              className="h-16 w-16 object-contain"
              onError={() => setImageFailed(true)}
            />
          </div>
        ) : (
          <img
            src={displayImageUrl}
            alt=""
            className="h-56 w-full rounded-t-lg object-cover"
            onError={() => setImageFailed(true)}
          />
        ))}
      <div className={`flex flex-col gap-3 p-6 ${showImage ? 'pt-6' : ''}`}>
        <span className="text-xs font-semibold uppercase tracking-wide text-brand-500">
          {source_name}
        </span>
        <h3 className="font-serif text-xl font-semibold leading-snug text-brand-50">{title}</h3>
        <p className="line-clamp-2 text-sm text-brand-300">{hook}</p>
        <span className="text-xs text-brand-500">{formattedDate}</span>
      </div>
    </div>
  );
}
