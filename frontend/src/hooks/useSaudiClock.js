import { useState, useEffect } from 'react';

// Live-updating clock showing the current date/time in Saudi Arabia
// (Asia/Riyadh timezone), updating every second.
export function useSaudiClock() {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  const options = { timeZone: 'Asia/Riyadh', hour12: true };
  const date = now.toLocaleDateString('en-US', { ...options, month: 'numeric', day: 'numeric', year: 'numeric' });
  const time = now.toLocaleTimeString('en-US', { ...options, hour: 'numeric', minute: '2-digit', second: '2-digit' });

  return { date, time };
}
