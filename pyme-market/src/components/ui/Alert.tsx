import type { ReactNode } from 'react';
import { clsx } from 'clsx';
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

interface AlertProps {
  readonly children: ReactNode;
  readonly variant?: 'success' | 'error' | 'warning' | 'info';
  readonly className?: string;
  readonly title?: string;
}

const icons = {
  success: CheckCircleIcon,
  error: XCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
};

const variants = {
  success: {
    container: 'bg-green-50 border-green-200 text-green-800',
    icon: 'text-green-400',
    title: 'text-green-800',
  },
  error: {
    container: 'bg-red-50 border-red-200 text-red-800',
    icon: 'text-red-400',
    title: 'text-red-800',
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    icon: 'text-yellow-400',
    title: 'text-yellow-800',
  },
  info: {
    container: 'bg-blue-50 border-blue-200 text-blue-800',
    icon: 'text-blue-400',
    title: 'text-blue-800',
  },
};

export function Alert({ children, variant = 'info', className, title }: AlertProps) {
  const Icon = icons[variant];
  const styles = variants[variant];

  return (
    <div
      className={clsx(
        'rounded-md border p-4',
        styles.container,
        className
      )}
    >
      <div className="flex">
        <Icon className={clsx('h-5 w-5 flex-shrink-0', styles.icon)} />
        <div className="ml-3">
          {title && (
            <h3 className={clsx('text-sm font-medium', styles.title)}>
              {title}
            </h3>
          )}
          <div className={clsx('text-sm', title ? 'mt-1' : '')}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
