import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useForm } from '../../hooks/useForm';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Alert } from '../ui/Alert';
import { ValidationService } from '../../services/validationService';
import { config } from '../../config/app';

export function ForgotPasswordForm() {
  const { forgotPassword, isLoading, error, resetError } = useAuth();
  const [successMessage, setSuccessMessage] = useState<string>('');

  const { isSubmitting, handleSubmit, getFieldProps } = useForm({
    initialValues: {
      email: '',
    },
    validationRules: {
      email: {
        required: true,
        custom: (value) => ValidationService.validateEmail(value),
      },
    },
    onSubmit: async (values) => {
      resetError();
      setSuccessMessage('');
      try {
        const message = await forgotPassword({ email: values.email });
        setSuccessMessage(message);
      } catch {
        // Error is handled by the auth context
      }
    },
  });

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert variant="error" title="Error">
          {error.message}
        </Alert>
      )}

      {successMessage && (
        <Alert variant="success" title="Contraseña restablecida">
          <div className="space-y-2">
            <p>{successMessage}</p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 mt-3">
              <p className="text-sm text-yellow-800">
                <strong>Importante:</strong> Tu contraseña temporal es:{' '}
                <code className="font-mono bg-yellow-100 px-1 py-0.5 rounded">
                  {config.auth.defaultPassword}
                </code>
              </p>
              <p className="text-sm text-yellow-700 mt-1">
                Por seguridad, te recomendamos cambiarla inmediatamente después de
                iniciar sesión.
              </p>
            </div>
          </div>
        </Alert>
      )}

      <div className="text-sm text-gray-600 text-center mb-4">
        Ingresa tu email y restableceremos tu contraseña a una temporal que
        podrás cambiar después de iniciar sesión.
      </div>

      <Input
        label="Email"
        type="email"
        placeholder="tu@email.com"
        autoComplete="email"
        {...getFieldProps('email')}
      />

      <Button
        type="submit"
        variant="primary"
        size="lg"
        className="w-full"
        isLoading={isSubmitting || isLoading}
      >
        Restablecer contraseña
      </Button>

      <div className="text-center space-y-2">
        <div>
          <Link
            to="/auth/login"
            className="text-sm text-blue-600 hover:text-blue-500"
          >
            ← Volver al inicio de sesión
          </Link>
        </div>
        <div>
          <span className="text-sm text-gray-600">
            ¿No tienes cuenta?{' '}
            <Link
              to="/auth/register"
              className="text-blue-600 hover:text-blue-500 font-medium"
            >
              Regístrate aquí
            </Link>
          </span>
        </div>
      </div>
    </form>
  );
}
