import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useForm } from '../../hooks/useForm';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Alert } from '../ui/Alert';
import { ValidationService } from '../../services/validationService';
import toast from 'react-hot-toast';

export function LoginForm() {
  const { login, isLoading, error, resetError } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);

  const { isSubmitting, handleSubmit, getFieldProps } = useForm({
    initialValues: {
      email: '',
      password: '',
    },
    validationRules: {
      email: {
        required: true,
        custom: (value) => ValidationService.validateEmail(value),
      },
      password: {
        required: true,
        custom: (value) => ValidationService.validatePassword(value),
      },
    },
    onSubmit: async (values) => {
      resetError();
      try {
        await login({
          email: values.email,
          password: values.password,
        });
        toast.success('¡Bienvenido! Has iniciado sesión correctamente');
        navigate('/dashboard');
      } catch (error) {
        // Error is handled by the auth context
        toast.error('Error al iniciar sesión. Verifica tus credenciales');
      }
    },
  });

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert variant="error" title="Error al iniciar sesión">
          {error.message}
        </Alert>
      )}

      <Input
        label="Email"
        type="email"
        placeholder="tu@email.com"
        autoComplete="email"
        {...getFieldProps('email')}
      />

      <div className="relative">
        <Input
          label="Contraseña"
          type={showPassword ? 'text' : 'password'}
          placeholder="Tu contraseña"
          autoComplete="current-password"
          {...getFieldProps('password')}
        />
        <button
          type="button"
          className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
          onClick={() => setShowPassword(!showPassword)}
        >
          <span className="text-sm text-gray-500">
            {showPassword ? 'Ocultar' : 'Mostrar'}
          </span>
        </button>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm">
          <Link
            to="/auth/forgot-password"
            className="text-blue-600 hover:text-blue-500"
          >
            ¿Olvidaste tu contraseña?
          </Link>
        </div>
      </div>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        className="w-full"
        isLoading={isSubmitting || isLoading}
      >
        Iniciar sesión
      </Button>

      <div className="text-center">
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
    </form>
  );
}
