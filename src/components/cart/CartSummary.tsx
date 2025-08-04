import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../../hooks/useCart';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { orderService } from '../../services/orderService';
import { cartService } from '../../services/cartService';
import toast from 'react-hot-toast';
import { ReceiptView } from './ReceiptView';

export function CartSummary() {
  const { cart, clearCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'cash' | 'transfer'>('card');
  const [purchaseSummary, setPurchaseSummary] = useState<string | null>(null);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const handleCheckout = async () => {
    if (!user?.id) {
      toast.error('Debes iniciar sesión para realizar la compra');
      return;
    }

    if (cart.items.length === 0) {
      toast.error('El carrito está vacío');
      return;
    }

    try {
      setIsProcessing(true);
      toast.loading('Procesando tu compra...');

      let serverCart = await cartService.getActiveCart(user.id);
      if (!serverCart) {
        serverCart = await cartService.createCart(user.id);
      }

      try {
        await cartService.syncCartWithServer(cart, serverCart.cartId);
      } catch (error) {
        console.error('Error syncing cart:', error);
        toast.error('Error al sincronizar el carrito. Por favor, intenta nuevamente.');
        return;
      }

      const purchase = await orderService.createPurchaseFromCart(
        cart,
        user.id,
        serverCart.cartId,
        paymentMethod
      );

      await orderService.generateReceipt(purchase.purchaseId);
      const formattedReceipt = await orderService.getFormattedReceipt(purchase.purchaseId);
      setPurchaseSummary(formattedReceipt);

      clearCart();

      toast.dismiss();
      toast.success('¡Compra realizada con éxito!');
    } catch (error: any) {
      console.error('Error processing checkout:', error);
      toast.dismiss();

      if (error.status === 404) {
        toast.error('Error al procesar la compra. Carrito no encontrado.');
      } else if (error.status === 400) {
        toast.error(error.message || 'Error al procesar la compra. Verifica los datos.');
      } else {
        toast.error('Error al procesar la compra. Por favor, intenta nuevamente.');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCloseSummary = () => {
    setPurchaseSummary(null);
    navigate('/dashboard/catalog');
  };

  return (
    <>
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Resumen del carrito
        </h2>

        <div className="space-y-4">
          <div className="flex justify-between text-base text-gray-600">
            <span>Subtotal</span>
            <span>{formatPrice(cart.totalPrice)}</span>
          </div>

          <div className="flex justify-between text-base text-gray-600">
            <span>IVA (19%)</span>
            <span>{formatPrice(cart.totalPrice * 0.19)}</span>
          </div>

          <div className="flex justify-between text-base text-gray-600">
            <span>Envío</span>
            <span>Gratis</span>
          </div>

          <div className="flex justify-between text-lg font-semibold text-gray-900 pt-4 border-t">
            <span>Total</span>
            <span>{formatPrice(cart.totalPrice * 1.19)}</span>
          </div>

          {cart.items.length > 0 && (
            <div className="pt-4">
              <label htmlFor="paymentMethod" className="block text-sm font-medium text-gray-700 mb-2">
                Método de pago
              </label>
              <select
                id="paymentMethod"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value as 'card' | 'cash' | 'transfer')}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                disabled={isProcessing}
              >
                <option value="card">Tarjeta de crédito/débito</option>
                <option value="cash">Efectivo</option>
                <option value="transfer">Transferencia bancaria</option>
              </select>
            </div>
          )}

          <div className="space-y-2 pt-4">
            <Button
              variant="primary"
              className="w-full"
              onClick={handleCheckout}
              disabled={cart.items.length === 0 || isProcessing}
            >
              {isProcessing ? 'Procesando...' : 'Proceder al pago'}
            </Button>

            {cart.items.length > 0 && (
              <Button
                variant="ghost"
                className="w-full text-red-600 hover:text-red-500"
                onClick={clearCart}
                disabled={isProcessing}
              >
                Vaciar carrito
              </Button>
            )}
          </div>

          {cart.items.length > 0 && (
            <p className="text-sm text-gray-500 mt-4">
              Los precios y la disponibilidad están sujetos a cambios. El carrito se actualiza automáticamente.
            </p>
          )}
        </div>
      </Card>

      {purchaseSummary && (
        <ReceiptView
          receipt={purchaseSummary}
          onClose={handleCloseSummary}
        />
      )}
    </>
  );
}