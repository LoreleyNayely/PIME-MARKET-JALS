import { DashboardLayout } from '../components/common/DashboardLayout';
import { ChatContainer } from '../components/chat/ChatContainer';

export function ChatPage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Chat de Soporte
          </h1>
          <p className="mt-2 text-gray-600">
            Comunícate en tiempo real con otros usuarios y nuestro equipo de soporte
          </p>
        </div>

        <ChatContainer />
      </div>
    </DashboardLayout>
  );
}