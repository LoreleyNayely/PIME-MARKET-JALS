import { Link } from 'react-router-dom';
import { useCart } from '../hooks/useCart';
import { DashboardLayout } from '../components/common/DashboardLayout';
import { CartItem } from '../components/cart/CartItem';
import { CartSummary } from '../components/cart/CartSummary';
import { Button } from '../components/ui/Button';
import { ShoppingBagIcon } from '@heroicons/react/24/outline';

export function CartPage() {
  const { cart } = useCart();

  if (cart.items.length === 0) {
    return (
      <DashboardLayout>
        <div className="min-h-screen bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="text-center">
              <ShoppingBagIcon className="mx-auto h-16 w-16 text-gray-400" />
              <h2 className="mt-4 text-2xl font-bold text-gray-900">
                Tu carrito está vacío
              </h2>
              <p className="mt-2 text-gray-600">
                Parece que aún no has agregado ningún producto a tu carrito.
              </p>
              <div className="mt-6">
                <Link to="/dashboard/catalog">
                  <Button variant="primary">
                    Ir al catálogo
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Mi Carrito
            </h1>
            <p className="text-gray-600">
              {cart.totalItems} {cart.totalItems === 1 ? 'producto' : 'productos'} en tu carrito
            </p>
          </div>

          <div className="lg:grid lg:grid-cols-12 lg:gap-8">
            <div className="lg:col-span-8">
              <div className="bg-white rounded-lg shadow">
                <div className="p-6 space-y-4">
                  {cart.items.map((item) => (
                    <CartItem key={item.productId} item={item} />
                  ))}
                </div>
              </div>

              <div className="mt-6">
                <Link to="/dashboard/catalog">
                  <Button variant="secondary">
                    Seguir comprando
                  </Button>
                </Link>
              </div>
            </div>

            <div className="lg:col-span-4 mt-8 lg:mt-0">
              <CartSummary />
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}