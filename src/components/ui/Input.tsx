import { forwardRef } from 'react';
import { clsx } from 'clsx';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  touched?: boolean;
  helperText?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    label,
    error,
    touched,
    helperText,
    id,
    ...props
  }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substring(2, 11)}`;
    const hasError = touched && error;

    const inputClasses = clsx(
      [
        'block',
        'w-full',
        'rounded-md',
        'border-0',
        'py-1.5',
        'px-3',
        'text-gray-900',
        'shadow-sm',
        'ring-1',
        'ring-inset',
        'placeholder:text-gray-400',
        'focus:ring-2',
        'focus:ring-inset',
        'sm:text-sm',
        'sm:leading-6',
        'transition-colors',
      ],
      hasError
        ? [
          'ring-red-300',
          'focus:ring-red-500',
        ]
        : [
          'ring-gray-300',
          'focus:ring-blue-600',
        ],
      className
    );

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium leading-6 text-gray-900 mb-1"
          >
            {label}
          </label>
        )}

        <input
          ref={ref}
          id={inputId}
          className={inputClasses}
          {...props}
        />

        {hasError && (
          <p className="mt-1 text-sm text-red-600">
            {error}
          </p>
        )}

        {helperText && !hasError && (
          <p className="mt-1 text-sm text-gray-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
