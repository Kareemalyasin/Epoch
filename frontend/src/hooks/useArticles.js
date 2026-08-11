import { useState, useEffect } from 'react';
import { fetchGroupedArticles } from '../api/articles';

// Fetches all articles once on mount and exposes loading/error states so
// components can render appropriately (spinner, error message, or actual content).
export function useArticles() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchGroupedArticles()
      .then((result) => {
        setData(result);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { data, loading, error };
}
