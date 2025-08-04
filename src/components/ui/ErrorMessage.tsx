import React from 'react';
import { Button } from './Button';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry, className = '' }) => {
  return (
    <div className={`bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative ${className}`} role="alert">
      <span className="block sm:inline">{message}</span>
      {onRetry && (
        <div className="mt-2">
          <Button onClick={onRetry} variant="secondary">
            Reintentar
          </Button>
        </div>
      )}
    </div>
  );
};