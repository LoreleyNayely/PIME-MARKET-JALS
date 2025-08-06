import { useState, useEffect } from 'react';
import { DashboardLayout } from '../components/common/DashboardLayout';
import { OrderItem } from '../components/orders/OrderItem';
import { useAuth } from '../hooks/useAuth';
import { orderService } from '../services/orderService';
import type { UserPurchase } from '../services/orderService';
import { ShoppingBagIcon } from '@heroicons/react/24/outline';

export function OrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState<UserPurchase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadOrders = async () => {
      if (!user?.id) return;

      try {
        setIsLoading(true);
        setError(null);
        const userOrders = await orderService.getUserPurchases(user.id);
        setOrders(userOrders.sort((a, b) => 
          new Date(b.purchasedAt).getTime() - new Date(a.purchasedAt).getTime()
        ));
      } catch (error) {
        console.error('Error loading orders:', error);
        setError('No se pudieron cargar las órdenes. Por favor, intenta nuevamente.');
      } finally {
        setIsLoading(false);
      }
    };

    loadOrders();
  }, [user?.id]);

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              Mis Órdenes
            </h1>
            <p className="mt-2 text-gray-600">
              Historial de todas tus compras
            </p>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-blue-600" />
              <p className="mt-2 text-gray-600">Cargando órdenes...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600">{error}</p>
            </div>
          ) : orders.length === 0 ? (
            <div className="text-center py-12">
              <ShoppingBagIcon className="mx-auto h-16 w-16 text-gray-400" />
              <h2 className="mt-4 text-lg font-medium text-gray-900">
                No tienes órdenes aún
              </h2>
              <p className="mt-2 text-gray-600">
                Tus compras aparecerán aquí cuando realices alguna.
              </p>
            </div>
          ) : (
            <div className="grid gap-6">
              {orders.map((order) => (
                <OrderItem key={order.purchaseId} order={order} />
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}