import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  fullScreen?: boolean;
  size?: number;
  text?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  fullScreen = false, 
  size = 24, 
  text 
}) => {
  const content = (
    <div className="flex flex-col items-center justify-center gap-3">
      <Loader2 className="animate-spin text-aria-500" size={size} />
      {text && <p className="text-sm text-slate-400">{text}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-surface-950/80 backdrop-blur-sm z-50 flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};
