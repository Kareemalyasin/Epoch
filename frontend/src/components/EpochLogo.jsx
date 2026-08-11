export default function EpochLogo({ className = "h-8 w-8" }) {
  return (
    <svg viewBox="0 0 120 120" className={className} xmlns="http://www.w3.org/2000/svg">
      <circle cx="60" cy="60" r="42" fill="none" stroke="var(--color-accent-500)" strokeWidth="7" />
      <circle cx="60" cy="18" r="9" fill="var(--color-accent-500)" />
    </svg>
  );
}
