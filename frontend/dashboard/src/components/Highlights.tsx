'use client';

import { useState, useEffect } from 'react';

interface HighlightsProps {
  highlights: string[];
}

export default function Highlights({ highlights }: HighlightsProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (highlights.length <= 1) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % highlights.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [highlights.length]);

  if (!highlights.length) return null;

  return (
    <div className="bg-gradient-to-r from-solana-purple/20 to-solana-green/20 rounded-xl border border-white/10 p-4 overflow-hidden">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-lg">✨</span>
          <span className="text-solana-green font-semibold text-sm uppercase tracking-wider">
            Insights
          </span>
        </div>
        
        <div className="relative flex-1 overflow-hidden h-6">
          {highlights.map((highlight, index) => (
            <div
              key={index}
              className={`absolute inset-0 flex items-center transition-all duration-500 ${
                index === currentIndex
                  ? 'opacity-100 translate-y-0'
                  : 'opacity-0 translate-y-4'
              }`}
            >
              <p className="text-white truncate">{highlight}</p>
            </div>
          ))}
        </div>

        <div className="flex gap-1 shrink-0">
          {highlights.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentIndex
                  ? 'bg-solana-green'
                  : 'bg-white/20 hover:bg-white/40'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
