import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useForm } from '../../hooks/useForm';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Alert } from '../ui/Alert';
import { ValidationService } from '../../services/validationService';

export function RegisterForm() {
  const { register, isLoading, error, resetError } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { isSubmitting, handleSubmit, getFieldProps, formState } = useForm({
    initialValues: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
    validationRules: {
      name: {
        required: true,
        custom: (value) => ValidationService.validateName(value),
      },
      email: {
        required: true,
        custom: (value) => ValidationService.validateEmail(value),
      },
      password: {
        required: true,
        custom: (value) => ValidationService.validatePassword(value),
      },
      confirmPassword: {
        required: true,
        custom: (value) => ValidationService.validateConfirmPassword(
          formState.password?.value || '',
          value
        ),
      },
    },
    onSubmit: async (values) => {
      resetError();
      try {
        await register({
          name: values.name,
          email: values.email,
          password: values.password,
          confirmPassword: values.confirmPassword,
        });
        navigate('/dashboard');
      } catch {
        // Error is handled by the auth context
      }
    },
  });

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert variant="error" title="Error al registrarse">
          {error.message}
        </Alert>
      )}

      <Input
        label="Nombre completo"
        type="text"
        placeholder="Tu nombre completo"
        autoComplete="name"
        {...getFieldProps('name')}
      />

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
          placeholder="Mínimo 6 caracteres"
          autoComplete="new-password"
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

      <div className="relative">
        <Input
          label="Confirmar contraseña"
          type={showConfirmPassword ? 'text' : 'password'}
          placeholder="Repite tu contraseña"
          autoComplete="new-password"
          {...getFieldProps('confirmPassword')}
        />
        <button
          type="button"
          className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
        >
          <span className="text-sm text-gray-500">
            {showConfirmPassword ? 'Ocultar' : 'Mostrar'}
          </span>
        </button>
      </div>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        className="w-full"
        isLoading={isSubmitting || isLoading}
      >
        Crear cuenta
      </Button>

      <div className="text-center">
        <span className="text-sm text-gray-600">
          ¿Ya tienes cuenta?{' '}
          <Link
            to="/auth/login"
            className="text-blue-600 hover:text-blue-500 font-medium"
          >
            Inicia sesión aquí
          </Link>
        </span>
      </div>
    </form>
  );
}
