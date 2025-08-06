import { AuthLayout } from '../../components/auth/AuthLayout';
import { RegisterForm } from '../../components/auth/RegisterForm';

export function RegisterPage() {
  return (
    <AuthLayout
      title="Crear cuenta"
      subtitle="Únete a la comunidad de PYME Market"
    >
      <RegisterForm />
    </AuthLayout>
  );
}
