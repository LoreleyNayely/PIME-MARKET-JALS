import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DashboardLayout } from '../components/common/DashboardLayout';
import { ProductForm } from '../components/products/ProductForm';
import { productService } from '../services/productService';
import type { Product } from '../interfaces/products';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import toast from 'react-hot-toast';

export function EditProductPage() {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);

  const loadProduct = useCallback(async (id: string) => {
    try {
      setLoading(true);
      const productData = await productService.getProductById(id);
      setProduct(productData);
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

  const handleSave = () => {
    toast.success('Producto actualizado correctamente');
    navigate('/dashboard/products');
  };

  const handleCancel = () => {
    navigate('/dashboard/products');
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Cargando producto...</span>
        </div>
      </DashboardLayout>
    );
  }

  if (!product) {
    return (
      <DashboardLayout>
        <Card className="text-center py-8">
          <p className="text-gray-500 mb-4">Producto no encontrado</p>
          <Button onClick={() => navigate('/dashboard/products')} variant="primary">
            Volver a productos
          </Button>
        </Card>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <ProductForm
          product={product}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      </div>
    </DashboardLayout>
  );
}