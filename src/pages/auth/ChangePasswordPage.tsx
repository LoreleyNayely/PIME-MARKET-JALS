import { useNavigate } from 'react-router-dom';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { ChangePasswordForm } from '../../components/auth/ChangePasswordForm';
import toast from 'react-hot-toast';

export function ChangePasswordPage() {
  const navigate = useNavigate();

  const handleSuccess = () => {
    toast.success('¡Contraseña cambiada exitosamente!');
    setTimeout(() => {
      navigate('/dashboard');
    }, 1500);
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  return (
    <AuthLayout
      title="Cambiar Contraseña"
      subtitle="Actualiza tu contraseña por una más segura"
    >
      <ChangePasswordForm
        onSuccess={handleSuccess}
        onCancel={handleCancel}
      />
    </AuthLayout>
  );
}