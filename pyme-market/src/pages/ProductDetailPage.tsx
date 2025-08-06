import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { DashboardLayout } from '../components/common/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { productService } from '../services/productService';
import type { CatalogProduct } from '../interfaces/products';
import { useCart } from '../hooks/useCart';
import {
  PencilIcon,
  ArrowLeftIcon,
  ShoppingCartIcon,
  StarIcon,
  ShareIcon,
  HeartIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid, HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';
import toast from 'react-hot-toast';

export function ProductDetailPage() {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<CatalogProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [isFavorite, setIsFavorite] = useState(false);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const { addToCart } = useCart();

  const loadProduct = useCallback(async (id: string) => {
    try {
      setLoading(true);
      const productData = await productService.getProductById(id);
      const catalogProduct: CatalogProduct = {
        productId: productData.productId,
        name: productData.name,
        description: productData.description || '',
        price: productData.price,
        stockQuantity: productData.stockQuantity,
        sku: productData.sku,
        isAvailable: productData.isActive && productData.stockQuantity > 0,
        imageUrl: undefined,
        category: undefined,
        rating: undefined,
        reviewsCount: undefined
      };
      setProduct(catalogProduct);
    } catch (error) {
      toast.error('Error al cargar el producto');
      console.error('Error loading product:', error);
      navigate('/dashboard/products');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    if (productId) {
      loadProduct(productId);
    }
  }, [productId, loadProduct]);

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
          <StarIconSolid key={i} className="h-5 w-5 text-yellow-400" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <div key={i} className="relative h-5 w-5">
            <StarIcon className="absolute h-5 w-5 text-gray-300" />
            <StarIconSolid
              className="absolute h-5 w-5 text-yellow-400"
              style={{ clipPath: 'inset(0 50% 0 0)' }}
            />
          </div>
        );
      } else {
        stars.push(
          <StarIcon key={i} className="h-5 w-5 text-gray-300" />
        );
      }
    }

    return stars;
  };

  const getStockStatus = () => {
    if (!product) return { color: 'text-gray-500', label: 'Cargando...' };

    if (product.stockQuantity === 0) {
      return { color: 'text-red-600', label: 'Sin stock' };
    }
    if (product.stockQuantity <= 5) {
      return { color: 'text-yellow-600', label: `Solo ${product.stockQuantity} disponibles` };
    }
    return { color: 'text-green-600', label: 'En stock' };
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: product?.name,
          text: product?.description,
          url: window.location.href,
        });
      } catch (error) {
        console.error('Error sharing:', error);
      }
    } else {
      try {
        await navigator.clipboard.writeText(window.location.href);
        toast.success('URL copiada al portapapeles');
      } catch (error) {
        toast.error('Error al copiar URL');
      }
    }
  };

  const handleAddToCart = () => {
    if (!product) return;

    try {
      const productForCart = {
        productId: product.productId,
        name: product.name,
        description: product.description,
        price: product.price,
        stockQuantity: product.stockQuantity,
        sku: product.sku,
        isActive: product.isAvailable,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      addToCart(productForCart, quantity);
      toast.success(`${product.name} agregado al carrito`);
    } catch (error) {
      toast.error('Error al agregar al carrito');
    }
  };

  const toggleFavorite = () => {
    setIsFavorite(!isFavorite);
    toast.success(isFavorite ? 'Eliminado de favoritos' : 'Agregado a favoritos');
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-96">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!product) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Producto no encontrado</h2>
          <p className="text-gray-600 mb-8">El producto que buscas no existe o ha sido eliminado.</p>
          <Link to="/dashboard/products">
            <Button>Volver a productos</Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  const images = product.imageUrl ? [product.imageUrl] : [];
  const stockStatus = getStockStatus();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="secondary"
              onClick={() => navigate('/dashboard/products')}
              className="flex items-center space-x-2"
            >
              <ArrowLeftIcon className="h-4 w-4" />
              <span>Volver</span>
            </Button>
            <h1 className="text-2xl font-bold text-gray-900">{product.name}</h1>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="secondary"
              onClick={handleShare}
              className="flex items-center space-x-2"
            >
              <ShareIcon className="h-4 w-4" />
              <span>Compartir</span>
            </Button>
            <Link to={`/dashboard/products/${product.productId}/edit`}>
              <Button
                variant="secondary"
                className="flex items-center space-x-2"
              >
                <PencilIcon className="h-4 w-4" />
                <span>Editar</span>
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-4">
            <Card className="p-6">
              <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center mb-4">
                {images.length > 0 ? (
                  <img
                    src={images[selectedImageIndex]}
                    alt={product.name}
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <div className="text-gray-400 text-center">
                    <div className="w-24 h-24 mx-auto mb-4 bg-gray-200 rounded-lg flex items-center justify-center">
                      <span className="text-4xl">📦</span>
                    </div>
                    <p>Sin imagen</p>
                  </div>
                )}
              </div>

              {images.length > 1 && (
                <div className="flex space-x-2 overflow-x-auto">
                  {images.map((image, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedImageIndex(index)}
                      className={`flex-shrink-0 w-16 h-16 rounded-lg border-2 overflow-hidden ${selectedImageIndex === index ? 'border-blue-500' : 'border-gray-200'
                        }`}
                    >
                      <img
                        src={image}
                        alt={`${product.name} ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              )}
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="p-6">
              <div className="space-y-4">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h2>
                  <div className="flex items-center space-x-4">
                    <span className="text-3xl font-bold text-blue-600">
                      {formatPrice(product.price)}
                    </span>
                    <span className={`text-sm font-medium ${stockStatus.color}`}>
                      {stockStatus.label}
                    </span>
                  </div>
                </div>

                {product.rating && (
                  <div className="flex items-center space-x-2">
                    <div className="flex">
                      {renderStars(product.rating)}
                    </div>
                    <span className="text-sm text-gray-600">
                      {product.rating.toFixed(1)} ({product.reviewsCount} reseñas)
                    </span>
                  </div>
                )}

                <div className="border-t border-gray-200 pt-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Descripción</h3>
                  <p className="text-gray-600 leading-relaxed">
                    {product.description || 'Sin descripción disponible'}
                  </p>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Detalles del producto</h3>
                  <dl className="grid grid-cols-1 gap-3">
                    <div className="flex justify-between">
                      <dt className="text-gray-600">SKU:</dt>
                      <dd className="font-medium text-gray-900">{product.sku}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Stock disponible:</dt>
                      <dd className="font-medium text-gray-900">{product.stockQuantity} unidades</dd>
                    </div>
                    {product.category && (
                      <div className="flex justify-between">
                        <dt className="text-gray-600">Categoría:</dt>
                        <dd className="font-medium text-gray-900">{product.category}</dd>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Estado:</dt>
                      <dd className={`font-medium ${product.isAvailable ? 'text-green-600' : 'text-red-600'}`}>
                        {product.isAvailable ? 'Disponible' : 'No disponible'}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <label htmlFor="quantity" className="text-sm font-medium text-gray-700">
                    Cantidad:
                  </label>
                  <select
                    id="quantity"
                    value={quantity}
                    onChange={(e) => setQuantity(Number(e.target.value))}
                    className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={!product.isAvailable}
                  >
                    {Array.from({ length: Math.min(product.stockQuantity, 10) }, (_, i) => (
                      <option key={i + 1} value={i + 1}>
                        {i + 1}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex space-x-3">
                  <Button
                    onClick={handleAddToCart}
                    disabled={!product.isAvailable || product.stockQuantity === 0}
                    className="flex-1 flex items-center justify-center space-x-2"
                  >
                    <ShoppingCartIcon className="h-5 w-5" />
                    <span>Agregar al carrito</span>
                  </Button>

                  <Button
                    variant="secondary"
                    onClick={toggleFavorite}
                    className="flex items-center justify-center px-4"
                  >
                    {isFavorite ? (
                      <HeartIconSolid className="h-5 w-5 text-red-500" />
                    ) : (
                      <HeartIcon className="h-5 w-5" />
                    )}
                  </Button>
                </div>

                {!product.isAvailable && (
                  <p className="text-sm text-red-600 text-center">
                    Este producto no está disponible actualmente
                  </p>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}