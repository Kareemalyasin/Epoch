// Fallback image shown when an article has no scraped image_url, using
// Google's public favicon service to fetch each source's own icon.
export const SOURCE_LOGO_DOMAINS = {
  'OpenAI Blog': 'openai.com',
  'Google DeepMind Blog': 'deepmind.google',
  'Hugging Face Blog': 'huggingface.co',
  'TechCrunch AI': 'techcrunch.com',
  'VentureBeat AI': 'venturebeat.com',
  'GitHub Trending': 'github.com',
  'Anthropic Blog': 'anthropic.com',
  'Meta AI Blog': 'ai.meta.com',
};

export function getSourceLogoUrl(sourceName) {
  const domain = SOURCE_LOGO_DOMAINS[sourceName];
  if (!domain) return null;
  return `https://www.google.com/s2/favicons?domain=${domain}&sz=128`;
}
