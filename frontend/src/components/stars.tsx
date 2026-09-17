const STARS = "★★★★★";

/**
 * Five stars filled to `value` (0-5, half steps).
 *
 * Two identical glyph runs are stacked, and the filled one is clipped to a percentage
 * width. That renders any fraction, including halves, without needing per-star logic.
 */
export function Stars({ value, className = "" }: { value: number; className?: string }) {
  const pct = Math.max(0, Math.min(5, value)) * 20;
  return (
    <span className={`relative inline-block leading-none whitespace-nowrap ${className}`}>
      <span className="text-border">{STARS}</span>
      <span
        className="absolute inset-0 overflow-hidden whitespace-nowrap text-accent"
        style={{ width: `${pct}%` }}
      >
        {STARS}
      </span>
    </span>
  );
}

export function RatingBadge({ value, count }: { value: number | null; count: number }) {
  if (value === null || count === 0) {
    return <span className="text-sm text-muted">No ratings yet</span>;
  }
  return (
    <span className="flex items-center gap-2 text-sm">
      <Stars value={value} className="text-lg" />
      <span className="font-medium">{value.toFixed(2)}</span>
      <span className="text-muted">
        from {count} {count === 1 ? "review" : "reviews"}
      </span>
    </span>
  );
}
