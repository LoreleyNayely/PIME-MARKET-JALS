import { TrashIcon } from '@heroicons/react/24/outline';
import { useCart } from '../../hooks/useCart';
import { Button } from '../ui/Button';
import type { CartItem as CartItemType } from '../../interfaces/products';

interface CartItemProps {
  item: CartItemType;
}

export function CartItem({ item }: CartItemProps) {
  const { updateQuantity, removeFromCart } = useCart();

  const handleQuantityChange = (newQuantity: number) => {
    if (newQuantity === 0) {
      removeFromCart(item.productId);
    } else {
      updateQuantity(item.productId, newQuantity);
    }
  };

  return (
    <div className="flex items-center gap-4 py-4 border-b border-gray-200">
      <div className="w-24 h-24 flex-shrink-0 overflow-hidden rounded-md border border-gray-200">
        {item.product.imageUrl ? (
          <img
            src={item.product.imageUrl}
            alt={item.product.name}
            className="h-full w-full object-cover object-center"
          />
        ) : (
          <div className="h-full w-full bg-gray-100 flex items-center justify-center">
            <span className="text-2xl">📦</span>
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col">
        <div className="flex justify-between text-base font-medium text-gray-900">
          <h3>{item.product.name}</h3>
          <p className="ml-4">
            ${(item.product.price * item.quantity).toFixed(2)}
          </p>
        </div>
        <p className="mt-1 text-sm text-gray-500 line-clamp-1">
          {item.product.description}
        </p>

        <div className="flex items-center justify-between mt-2">
          <div className="flex items-center gap-2">
            <label htmlFor={`quantity-${item.productId}`} className="text-sm text-gray-600">
              Cantidad:
            </label>
            <select
              id={`quantity-${item.productId}`}
              value={item.quantity}
              onChange={(e) => handleQuantityChange(Number(e.target.value))}
              className="rounded-md border border-gray-300 text-base"
            >
              {Array.from(
                { length: Math.min(10, item.product.stockQuantity) },
                (_, i) => i + 1
              ).map((num) => (
                <option key={num} value={num}>
                  {num}
                </option>
              ))}
            </select>
          </div>

          <Button
            variant="ghost"
            onClick={() => removeFromCart(item.productId)}
            className="text-red-600 hover:text-red-500"
          >
            <TrashIcon className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}