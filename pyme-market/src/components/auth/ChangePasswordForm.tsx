import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useForm } from '../../hooks/useForm';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Alert } from '../ui/Alert';
import { ValidationService } from '../../services/validationService';

interface ChangePasswordFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function ChangePasswordForm({ onSuccess, onCancel }: ChangePasswordFormProps) {
  const { changePassword, isLoading, error, resetError } = useAuth();
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  const { isSubmitting, handleSubmit, getFieldProps } = useForm({
    initialValues: {
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: '',
    },
    validationRules: {
      currentPassword: {
        required: true,
        minLength: 6,
      },
      newPassword: {
        required: true,
        custom: (value) => ValidationService.validatePassword(value),
      },
      confirmNewPassword: {
        required: true,
        custom: (value, values) => {
          if (value !== values.newPassword) {
            return 'Las contraseñas no coinciden';
          }
          return null;
        },
      },
    },
    onSubmit: async (values) => {
      resetError();
      setSuccessMessage('');
      try {
        const message = await changePassword({
          currentPassword: values.currentPassword,
          newPassword: values.newPassword,
          confirmNewPassword: values.confirmNewPassword,
        });
        setSuccessMessage(message);

        setTimeout(() => {
          if (onSuccess) {
            onSuccess();
          }
        }, 2000);
      } catch {
        // Error is handled by the auth context
      }
    },
  });

  const togglePasswordVisibility = (field: keyof typeof showPasswords) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  return (
    <div className="max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <Alert variant="error" title="Error">
            {error.message}
          </Alert>
        )}

        {successMessage && (
          <Alert variant="success" title="Éxito">
            {successMessage}
          </Alert>
        )}

        <div className="relative">
          <Input
            label="Contraseña actual"
            type={showPasswords.current ? 'text' : 'password'}
            placeholder="Tu contraseña actual"
            autoComplete="current-password"
            {...getFieldProps('currentPassword')}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
            onClick={() => togglePasswordVisibility('current')}
          >
            <span className="text-sm text-gray-500">
              {showPasswords.current ? 'Ocultar' : 'Mostrar'}
            </span>
          </button>
        </div>

        <div className="relative">
          <Input
            label="Nueva contraseña"
            type={showPasswords.new ? 'text' : 'password'}
            placeholder="Tu nueva contraseña"
            autoComplete="new-password"
            {...getFieldProps('newPassword')}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
            onClick={() => togglePasswordVisibility('new')}
          >
            <span className="text-sm text-gray-500">
              {showPasswords.new ? 'Ocultar' : 'Mostrar'}
            </span>
          </button>
        </div>

        <div className="relative">
          <Input
            label="Confirmar nueva contraseña"
            type={showPasswords.confirm ? 'text' : 'password'}
            placeholder="Confirma tu nueva contraseña"
            autoComplete="new-password"
            {...getFieldProps('confirmNewPassword')}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
            onClick={() => togglePasswordVisibility('confirm')}
          >
            <span className="text-sm text-gray-500">
              {showPasswords.confirm ? 'Ocultar' : 'Mostrar'}
            </span>
          </button>
        </div>

        <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md">
          <p className="font-medium mb-1">Requisitos de la contraseña:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Mínimo 6 caracteres</li>
            <li>Al menos una letra mayúscula</li>
            <li>Al menos una letra minúscula</li>
            <li>Al menos un número</li>
          </ul>
        </div>

        <div className="flex gap-3">
          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="flex-1"
            isLoading={isSubmitting || isLoading}
          >
            Cambiar contraseña
          </Button>

          {onCancel && (
            <Button
              type="button"
              variant="secondary"
              size="lg"
              onClick={onCancel}
              disabled={isSubmitting || isLoading}
            >
              Cancelar
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}