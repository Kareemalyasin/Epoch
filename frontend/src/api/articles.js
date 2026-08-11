// The single place that knows how to reach the backend's grouped-articles
// endpoint, so the rest of the app doesn't need to know the URL or fetch details.

const API_URL = import.meta.env.VITE_API_URL;

export async function fetchGroupedArticles() {
  const response = await fetch(`${API_URL}/articles/grouped`);

  if (!response.ok) {
    throw new Error(`Failed to fetch grouped articles: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
