import { AuthLayout } from '../../components/auth/AuthLayout';
import { ForgotPasswordForm } from '../../components/auth/ForgotPasswordForm';

export function ForgotPasswordPage() {
  return (
    <AuthLayout
      title="Recuperar contraseña"
      subtitle="Te ayudamos a recuperar el acceso a tu cuenta"
    >
      <ForgotPasswordForm />
    </AuthLayout>
  );
}
