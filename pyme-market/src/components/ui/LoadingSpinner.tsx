import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', color = 'blue' }) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-24 w-24',
  };

  return (
    <div
      className={`animate-spin rounded-full border-t-2 border-${color}-500 ${sizeClasses[size]}`}
      style={{ borderRightColor: 'transparent' }}
    ></div>
  );
};