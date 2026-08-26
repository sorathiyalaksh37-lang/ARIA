// src/components/ui/LoadingSpinner.tsx
import React from 'react';
import { clsx } from 'clsx';

interface Props {
  size?:       'sm' | 'md' | 'lg';
  fullscreen?: boolean;
  label?:      string;
}

const sizes = {
  sm:  'w-4 h-4 border-2',
  md:  'w-8 h-8 border-2',
  lg:  'w-12 h-12 border-[3px]',
};

const LoadingSpinner: React.FC<Props> = ({
  size = 'md',
  fullscreen = false,
  label,
}) => {
  const spinner = (
    <div className="flex flex-col items-center gap-3">
      <div
        className={clsx(
          'rounded-full border-transparent border-t-aria-500 animate-spin',
          sizes[size]
        )}
        style={{ borderTopColor: undefined }}
      >
        <span className="sr-only">{label ?? 'Loading…'}</span>
      </div>
      {label && (
        <p className="text-sm text-slate-400 animate-pulse">{label}</p>
      )}
    </div>
  );

  if (fullscreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-surface-950">
        {spinner}
      </div>
    );
  }

  return spinner;
};

export default LoadingSpinner;
