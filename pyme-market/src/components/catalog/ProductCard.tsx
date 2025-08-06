import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../../hooks/useCart';
import type { CatalogProduct } from '../../interfaces/products';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import {
  ShoppingCartIcon,
  StarIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

interface ProductCardProps {
  product: CatalogProduct;
}

export function ProductCard({ product }: ProductCardProps) {
  const { addToCart, isInCart, getItemQuantity } = useCart();
  const [quantity, setQuantity] = useState(1);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <StarIconSolid key={i} className="h-4 w-4 text-yellow-400" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <div key={i} className="relative h-4 w-4">
            <StarIcon className="absolute h-4 w-4 text-gray-300" />
            <StarIconSolid
              className="absolute h-4 w-4 text-yellow-400"
              style={{ clipPath: 'inset(0 50% 0 0)' }}
            />
          </div>
        );
      } else {
        stars.push(
          <StarIcon key={i} className="h-4 w-4 text-gray-300" />
        );
      }
    }

    return stars;
  };

  const handleAddToCart = () => {
    const productForCart = {
      productId: product.productId,
      name: product.name,
      description: product.description,
      price: product.price,
      stockQuantity: product.stockQuantity,
      sku: product.sku,
      isActive: product.isAvailable,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    addToCart(productForCart, quantity);
    setQuantity(1);
  };

  const getStockStatus = () => {
    if (product.stockQuantity === 0) {
      return { color: 'text-red-600', label: 'Sin stock' };
    }
    if (product.stockQuantity <= 5) {
      return { color: 'text-yellow-600', label: `Solo ${product.stockQuantity} disponibles` };
    }
    return { color: 'text-green-600', label: 'En stock' };
  };

  const stockStatus = getStockStatus();
  const currentCartQuantity = getItemQuantity(product.productId);

  return (
    <Card className="group hover:shadow-lg transition-shadow duration-200">
      <div className="relative">
        <div className="aspect-square bg-gray-100 rounded-t-lg overflow-hidden">
          {product.imageUrl ? (
            <img
              src={product.imageUrl}
              alt={product.name}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <span className="text-gray-400 text-4xl">📦</span>
            </div>
          )}
        </div>

        {product.stockQuantity <= 5 && product.stockQuantity > 0 && (
          <div className="absolute top-2 left-2 bg-yellow-500 text-white text-xs px-2 py-1 rounded-full">
            ¡Últimas unidades!
          </div>
        )}

        {product.stockQuantity === 0 && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-t-lg">
            <span className="bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium">
              Sin stock
            </span>
          </div>
        )}
      </div>

      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-semibold text-gray-900 line-clamp-2 mb-1">
            {product.name}
          </h3>

          {product.description && (
            <p className="text-sm text-gray-600 line-clamp-2 mb-2">
              {product.description}
            </p>
          )}

          {product.rating && (
            <div className="flex items-center gap-2 mb-2">
              <div className="flex items-center">
                {renderStars(product.rating)}
              </div>
              <span className="text-sm text-gray-500">
                {product.rating.toFixed(1)} ({product.reviewsCount} reseñas)
              </span>
            </div>
          )}

          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl font-bold text-blue-600">
              {formatPrice(product.price)}
            </span>
            <span className={`text-sm font-medium ${stockStatus.color}`}>
              {stockStatus.label}
            </span>
          </div>
        </div>

        <div className="space-y-3">
          {product.isAvailable && (
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-700">Cantidad:</label>
              <select
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                className="border border-gray-300 rounded px-2 py-1 text-sm"
                disabled={product.stockQuantity === 0}
              >
                {Array.from({ length: Math.min(10, product.stockQuantity) }, (_, i) => (
                  <option key={i + 1} value={i + 1}>
                    {i + 1}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="flex gap-2">
            <Link to={`/dashboard/products/${product.productId}`} className="flex-1">
              <Button
                variant="secondary"
                className="w-full flex items-center justify-center gap-2"
              >
                <EyeIcon className="h-4 w-4" />
                Ver
              </Button>
            </Link>

            {product.isAvailable ? (
              <Button
                variant="primary"
                onClick={handleAddToCart}
                className="flex-1 flex items-center justify-center gap-2"
                disabled={quantity > product.stockQuantity - currentCartQuantity}
              >
                <ShoppingCartIcon className="h-4 w-4" />
                {isInCart(product.productId) ? 'Agregar más' : 'Al carrito'}
              </Button>
            ) : (
              <Button
                variant="secondary"
                disabled
                className="flex-1 flex items-center justify-center gap-2 opacity-50"
              >
                No disponible
              </Button>
            )}
          </div>

          {currentCartQuantity > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
              <p className="text-sm text-blue-800 text-center">
                {currentCartQuantity} en el carrito
              </p>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}