import { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { ReceiptView } from '../cart/ReceiptView';
import { orderService } from '../../services/orderService';
import type { UserPurchase } from '../../services/orderService';
import { DocumentTextIcon, EyeIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface OrderItemProps {
  order: UserPurchase;
}

export function OrderItem({ order }: OrderItemProps) {
  const [receipt, setReceipt] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return { text: 'Completada', color: 'text-green-600 bg-green-100' };
      case 'pending':
        return { text: 'Pendiente', color: 'text-yellow-600 bg-yellow-100' };
      case 'cancelled':
        return { text: 'Cancelada', color: 'text-red-600 bg-red-100' };
      default:
        return { text: status, color: 'text-gray-600 bg-gray-100' };
    }
  };

  const handleViewReceipt = async () => {
    try {
      setIsLoading(true);
      let formattedReceipt;

      try {
        formattedReceipt = await orderService.getFormattedReceipt(order.purchaseId);
      } catch (error: any) {
        if (error.status === 404) {
          await orderService.generateReceipt(order.purchaseId);
          formattedReceipt = await orderService.getFormattedReceipt(order.purchaseId);
        } else {
          throw error;
        }
      }

      setReceipt(formattedReceipt);
    } catch (error) {
      console.error('Error loading receipt:', error);
      toast.error('Error al cargar el recibo. Por favor, intenta nuevamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const status = getStatusLabel(order.status);

  return (
    <>
      <Card className="overflow-hidden">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Orden #{order.purchaseNumber}
              </h3>
              <p className="text-sm text-gray-500">
                {formatDate(order.purchasedAt)}
              </p>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${status.color}`}>
              {status.text}
            </span>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Método de pago:</span>
              <span className="font-medium">{order.paymentMethod.toUpperCase()}</span>
            </div>

            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Subtotal:</span>
              <span>{formatPrice(order.totalAmount)}</span>
            </div>

            <div className="flex justify-between text-sm">
              <span className="text-gray-600">IVA (19%):</span>
              <span>{formatPrice(order.taxAmount)}</span>
            </div>

            {order.discountAmount > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Descuento:</span>
                <span className="text-green-600">-{formatPrice(order.discountAmount)}</span>
              </div>
            )}

            <div className="flex justify-between text-base font-semibold border-t pt-4">
              <span>Total:</span>
              <span>{formatPrice(order.finalAmount)}</span>
            </div>
          </div>

          <div className="mt-6 flex gap-3 justify-end">
            <Button
              variant="secondary"
              onClick={handleViewReceipt}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              {order.receiptId ? (
                <>
                  <DocumentTextIcon className="h-5 w-5" />
                  Ver recibo
                </>
              ) : (
                <>
                  <EyeIcon className="h-5 w-5" />
                  Ver detalles
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>

      {receipt && (
        <ReceiptView
          receipt={receipt}
          onClose={() => setReceipt(null)}
        />
      )}
    </>
  );
}