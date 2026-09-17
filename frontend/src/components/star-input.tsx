"use client";

import { Stars } from "@/components/stars";

/**
 * Half-star picker.
 *
 * A native range input is stretched invisibly over the stars, so dragging, clicking and
 * arrow keys all work, and screen readers get a real slider instead of a pile of divs.
 * The range counts half-stars (0-10); 0 means "not rated yet".
 */
export function StarInput({
  value,
  onChange,
  id = "rating",
}: {
  value: number;
  onChange: (value: number) => void;
  id?: string;
}) {
  return (
    <div className="flex items-center gap-3">
      {/* The range input itself is transparent, so the focus ring has to live on the
          wrapper or keyboard users would have no visible indicator at all. */}
      <div className="relative inline-flex rounded-sm px-1 focus-within:ring-2 focus-within:ring-accent">
        <Stars value={value} className="text-3xl" />
        <input
          id={id}
          type="range"
          min={0}
          max={10}
          step={1}
          value={value * 2}
          onChange={(event) => onChange(Number(event.target.value) / 2)}
          aria-label="Rating out of five stars"
          aria-valuetext={value === 0 ? "No rating" : `${value} out of 5 stars`}
          className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
        />
      </div>
      <span className="text-sm text-muted tabular-nums">
        {value === 0 ? "Drag or use arrow keys" : `${value.toFixed(1)} / 5`}
      </span>
    </div>
  );
}
