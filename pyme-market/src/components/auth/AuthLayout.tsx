import type { ReactNode } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';

interface AuthLayoutProps {
  readonly children: ReactNode;
  readonly title: string;
  readonly subtitle?: string;
}

export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            PYME Market
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Tu marketplace para pequeñas y medianas empresas
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-center">{title}</CardTitle>
            {subtitle && (
              <p className="text-center text-sm text-gray-600 mt-2">
                {subtitle}
              </p>
            )}
          </CardHeader>

          <CardContent>
            {children}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
