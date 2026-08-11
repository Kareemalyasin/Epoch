import { useState, useEffect } from 'react';

// Tracks scroll progress (0 to 1) down the page, used to drive an ambient
// glow effect that intensifies the further down the user scrolls.
export function useScrollGlow() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    function updateProgress() {
      const scrollY = window.scrollY;
      const maxScroll = document.body.scrollHeight - window.innerHeight;
      const newProgress = maxScroll > 0 ? Math.min(scrollY / maxScroll, 1) : 0;
      setProgress(newProgress);
    }

    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();

    return () => window.removeEventListener('scroll', updateProgress);
  }, []);

  return progress;
}
