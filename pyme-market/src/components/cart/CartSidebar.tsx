import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../../hooks/useCart';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import {
  ShoppingCartIcon,
  PlusIcon,
  MinusIcon,
  TrashIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

export function CartSidebar() {
  const { cart, updateQuantity, removeFromCart, getCartSummary } = useCart();
  const [isOpen, setIsOpen] = useState(false);
  const summary = getCartSummary();

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  if (cart.items.length === 0) {
    return (
      <div className="fixed top-20 right-4 z-50">
        <Button
          variant="primary"
          onClick={() => setIsOpen(!isOpen)}
          className="relative flex items-center gap-2"
        >
          <ShoppingCartIcon className="h-5 w-5" />
          <span className="hidden sm:inline">Carrito</span>
          <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            0
          </span>
        </Button>
      </div>
    );
  }

  return (
    <>
      <div className="fixed top-20 right-4 z-50">
        <Button
          variant="primary"
          onClick={() => setIsOpen(!isOpen)}
          className="relative flex items-center gap-2"
        >
          <ShoppingCartIcon className="h-5 w-5" />
          <span className="hidden sm:inline">Carrito</span>
          <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {cart.totalItems}
          </span>
        </Button>
      </div>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setIsOpen(false)}
          />

          <div className="fixed top-0 right-0 h-full w-96 bg-white shadow-xl z-50 transform transition-transform duration-300">
            <div className="flex flex-col h-full">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Mi Carrito ({cart.totalItems})
                  </h2>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setIsOpen(false)}
                  >
                    ✕
                  </Button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {cart.items.map((item) => (
                  <Card key={item.productId} className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
                        <span className="text-gray-400 text-xs">IMG</span>
                      </div>

                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 text-sm">
                          {item.product.name}
                        </h3>
                        <p className="text-sm text-gray-500 mb-2">
                          {formatPrice(item.product.price)}
                        </p>

                        <div className="flex items-center gap-2">
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => updateQuantity(item.productId, item.quantity - 1)}
                            className="p-1"
                          >
                            <MinusIcon className="h-3 w-3" />
                          </Button>

                          <span className="text-sm font-medium px-2">
                            {item.quantity}
                          </span>

                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => updateQuantity(item.productId, item.quantity + 1)}
                            className="p-1"
                            disabled={item.quantity >= item.product.stockQuantity}
                          >
                            <PlusIcon className="h-3 w-3" />
                          </Button>

                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => removeFromCart(item.productId)}
                            className="p-1 ml-2 text-red-600 hover:text-red-700"
                          >
                            <TrashIcon className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>

                      <div className="text-right">
                        <p className="font-medium text-gray-900">
                          {formatPrice(item.product.price * item.quantity)}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              <div className="border-t border-gray-200 p-4 space-y-4">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Subtotal:</span>
                    <span>{formatPrice(summary.subtotal)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Impuestos:</span>
                    <span>{formatPrice(summary.tax)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Envío:</span>
                    <span>
                      {summary.shipping === 0 ? 'Gratis' : formatPrice(summary.shipping)}
                    </span>
                  </div>
                  <div className="flex justify-between font-semibold text-lg pt-2 border-t">
                    <span>Total:</span>
                    <span>{formatPrice(summary.total)}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <Link to="/dashboard/cart" onClick={() => setIsOpen(false)}>
                    <Button variant="secondary" className="w-full">
                      Ver Carrito Completo
                    </Button>
                  </Link>

                  <Button variant="primary" className="w-full flex items-center justify-center gap-2">
                    Proceder al Checkout
                    <ArrowRightIcon className="h-4 w-4" />
                  </Button>
                </div>

                {summary.shipping === 0 && (
                  <p className="text-xs text-green-600 text-center">
                    ¡Envío gratis por compra mayor a $50!
                  </p>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}