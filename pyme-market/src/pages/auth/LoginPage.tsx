import { AuthLayout } from '../../components/auth/AuthLayout';
import { LoginForm } from '../../components/auth/LoginForm';

export function LoginPage() {
  return (
    <AuthLayout
      title="Iniciar sesión"
      subtitle="Accede a tu cuenta de PYME Market"
    >
      <LoginForm />
    </AuthLayout>
  );
}
