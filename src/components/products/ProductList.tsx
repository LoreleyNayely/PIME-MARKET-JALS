import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import type { Product, ProductFilters } from '../../interfaces/products';
import { productService } from '../../services/productService';
import { useAuth } from '../../hooks/useAuth';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface ProductListProps {
  onDelete?: (product: Product) => void;
  showActions?: boolean;
}

export function ProductList({ onDelete, showActions = true }: ProductListProps) {
  const { isAdmin } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<ProductFilters>({});
  const [showFilters, setShowFilters] = useState(false);

  const loadProducts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await productService.getAllProducts(filters);
      setProducts(response.products);
    } catch (error) {
      toast.error('Error al cargar productos');
      console.error('Error loading products:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const handleDelete = async (product: Product) => {
    if (!window.confirm(`¿Estás seguro de eliminar "${product.name}"?`)) {
      return;
    }

    try {
      await productService.deleteProduct(product.productId);
      toast.success('Producto eliminado correctamente');
      loadProducts();

      if (onDelete) {
        onDelete(product);
      }
    } catch (error) {
      toast.error('Error al eliminar producto');
      console.error('Error deleting product:', error);
    }
  };

  const handleRestore = async (product: Product) => {
    try {
      await productService.restoreProduct(product.productId);
      toast.success('Producto restaurado correctamente');
      loadProducts();
    } catch (error) {
      toast.error('Error al restaurar producto');
      console.error('Error restoring product:', error);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getStockStatus = (stock: number) => {
    if (stock === 0) return { color: 'text-red-600', label: 'Sin stock' };
    if (stock <= 5) return { color: 'text-yellow-600', label: 'Stock bajo' };
    return { color: 'text-green-600', label: 'En stock' };
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Cargando productos...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Gestión de Productos
          </h2>
          <p className="text-gray-600 mt-1">
            {products.length} producto{products.length !== 1 ? 's' : ''} encontrado{products.length !== 1 ? 's' : ''}
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            variant="secondary"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2"
          >
            <AdjustmentsHorizontalIcon className="h-4 w-4" />
            Filtros
          </Button>

          {isAdmin() && (
            <Link to="/dashboard/products/new">
              <Button variant="primary" className="flex items-center gap-2">
                <PlusIcon className="h-4 w-4" />
                Nuevo Producto
              </Button>
            </Link>
          )}
        </div>
      </div>

      {showFilters && (
        <Card className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Input
              label="Buscar"
              placeholder="Nombre, SKU o descripción..."
              value={filters.search || ''}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            />

            <Input
              label="Precio mínimo"
              type="number"
              placeholder="0.00"
              value={filters.minPrice || ''}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                minPrice: e.target.value ? parseFloat(e.target.value) : undefined
              }))}
            />

            <Input
              label="Precio máximo"
              type="number"
              placeholder="999.99"
              value={filters.maxPrice || ''}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                maxPrice: e.target.value ? parseFloat(e.target.value) : undefined
              }))}
            />

            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.includeInactive || false}
                  onChange={(e) => setFilters(prev => ({
                    ...prev,
                    includeInactive: e.target.checked
                  }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Incluir inactivos</span>
              </label>
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setFilters({})}
            >
              Limpiar filtros
            </Button>
          </div>
        </Card>
      )}

      {products.length === 0 ? (
        <Card className="text-center py-8">
          <p className="text-gray-500">No se encontraron productos</p>
          {isAdmin() && (
            <Link to="/dashboard/products/new" className="mt-4 inline-block">
              <Button variant="primary">Crear primer producto</Button>
            </Link>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {products.map((product) => {
            const stockStatus = getStockStatus(product.stockQuantity);

            return (
              <Card key={product.productId} className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {product.name}
                        </h3>
                        <p className="text-sm text-gray-500 mb-2">
                          SKU: {product.sku}
                        </p>
                        {product.description && (
                          <p className="text-gray-600 text-sm mb-3 max-w-2xl">
                            {product.description}
                          </p>
                        )}
                      </div>

                      {!product.isActive && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Inactivo
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Precio: </span>
                        <span className="font-medium text-green-600">
                          {formatPrice(product.price)}
                        </span>
                      </div>

                      <div>
                        <span className="text-gray-500">Stock: </span>
                        <span className={`font-medium ${stockStatus.color}`}>
                          {product.stockQuantity} unidades ({stockStatus.label})
                        </span>
                      </div>

                      <div>
                        <span className="text-gray-500">Actualizado: </span>
                        <span className="text-gray-700">
                          {new Date(product.updatedAt).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  {showActions && (
                    <div className="flex gap-2 lg:flex-col lg:items-end">
                      <Link to={`/dashboard/products/${product.productId}`}>
                        <Button
                          variant="secondary"
                          size="sm"
                          className="flex items-center gap-1"
                        >
                          <EyeIcon className="h-4 w-4" />
                          Ver
                        </Button>
                      </Link>

                      {isAdmin() && (
                        <>
                          <Link to={`/dashboard/products/${product.productId}/edit`}>
                            <Button
                              variant="secondary"
                              size="sm"
                              className="flex items-center gap-1"
                            >
                              <PencilIcon className="h-4 w-4" />
                              Editar
                            </Button>
                          </Link>

                          {product.isActive ? (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => handleDelete(product)}
                              className="flex items-center gap-1 text-red-600 hover:text-red-700 hover:bg-red-50"
                            >
                              <TrashIcon className="h-4 w-4" />
                              Eliminar
                            </Button>
                          ) : (
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => handleRestore(product)}
                              className="flex items-center gap-1"
                            >
                              Restaurar
                            </Button>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}