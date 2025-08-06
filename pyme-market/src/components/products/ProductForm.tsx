import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Product, ProductCreate, ProductUpdate } from '../../interfaces/products';
import { productService } from '../../services/productService';
import { useForm } from '../../hooks/useForm';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card } from '../ui/Card';
import { ValidationService } from '../../services/validationService';
import toast from 'react-hot-toast';

interface ProductFormProps {
  product?: Product;
  onSave?: (product: Product) => void;
  onCancel?: () => void;
}

export function ProductForm({ product, onSave, onCancel }: ProductFormProps) {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isEdit = !!product;

  const { formState, handleSubmit, setFieldValue, setFieldTouched, getFieldProps } = useForm({
    initialValues: {
      name: product?.name || '',
      description: product?.description || '',
      price: product?.price?.toString() || '',
      stockQuantity: product?.stockQuantity?.toString() || '',
      sku: product?.sku || '',
    },
    validationRules: {
      name: {
        required: true,
        minLength: 1,
        maxLength: 255,
      },
      description: {
        maxLength: 1000,
      },
      price: {
        required: true,
        custom: (value) => {
          const num = parseFloat(value);
          if (isNaN(num) || num <= 0) {
            return 'El precio debe ser mayor a 0';
          }
          if (!/^\d+(\.\d{1,2})?$/.test(value)) {
            return 'El precio puede tener máximo 2 decimales';
          }
          return null;
        },
      },
      stockQuantity: {
        required: true,
        custom: (value) => {
          const num = parseInt(value);
          if (isNaN(num) || num < 0) {
            return 'El stock debe ser 0 o mayor';
          }
          return null;
        },
      },
      sku: {
        required: true,
        minLength: 1,
        maxLength: 100,
        custom: (value) => ValidationService.validateSku(value),
      },
    },
    onSubmit: async (formValues) => {
      setIsSubmitting(true);
      try {
        const productData = {
          name: formValues.name.trim(),
          description: formValues.description?.trim() || undefined,
          price: parseFloat(formValues.price),
          stockQuantity: parseInt(formValues.stockQuantity),
          sku: formValues.sku.toUpperCase().trim(),
        };

        let savedProduct: Product;

        if (isEdit && product) {
          const updateData: ProductUpdate = {
            ...productData,
          };
          savedProduct = await productService.updateProduct(product.productId, updateData);
          toast.success('Producto actualizado correctamente');
        } else {
          const createData: ProductCreate = productData;
          savedProduct = await productService.createProduct(createData);
          toast.success('Producto creado correctamente');
        }

        if (onSave) {
          onSave(savedProduct);
        } else {
          navigate('/dashboard/products');
        }

      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Error al guardar producto';
        toast.error(errorMessage);
        console.error('Error saving product:', error);
      } finally {
        setIsSubmitting(false);
      }
    },
  });

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      navigate('/dashboard/products');
    }
  };

  const generateSku = () => {
    if (formState.name?.value) {
      const nameWords = formState.name.value
        .toUpperCase()
        .replace(/[^A-Z0-9\s]/g, '')
        .split(' ')
        .filter((word: string) => word.length > 0)
        .slice(0, 3);

      const baseSku = nameWords.join('-');
      const timestamp = Date.now().toString().slice(-4);
      const generatedSku = `${baseSku}-${timestamp}`;

      setFieldValue('sku', generatedSku);
    }
  };

  return (
    <Card className="max-w-2xl mx-auto">
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {isEdit ? 'Editar Producto' : 'Nuevo Producto'}
          </h2>
          <p className="text-gray-600 mt-1">
            {isEdit
              ? 'Actualiza la información del producto'
              : 'Completa la información para crear un nuevo producto'
            }
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Nombre del producto"
            placeholder="Ej: Laptop Dell Inspiron 15"
            required
            {...getFieldProps('name')}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descripción
            </label>
            <textarea
              rows={3}
              placeholder="Descripción detallada del producto..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              maxLength={1000}
              value={formState.description?.value || ''}
              onChange={(e) => setFieldValue('description', e.target.value)}
              onBlur={() => setFieldTouched('description')}
            />
            {formState.description?.error && (
              <p className="mt-1 text-sm text-red-600">{formState.description.error}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              {(formState.description?.value || '').length}/1000 caracteres
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Precio (USD)"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="99.99"
              required
              {...getFieldProps('price')}
            />

            <Input
              label="Stock inicial"
              type="number"
              min="0"
              placeholder="10"
              required
              {...getFieldProps('stockQuantity')}
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                SKU (Código del producto) *
              </label>
              {!isEdit && (
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={generateSku}
                  disabled={!formState.name?.value}
                >
                  Generar automático
                </Button>
              )}
            </div>
            <Input
              placeholder="PROD-001"
              required
              readOnly={isEdit}
              className={isEdit ? 'bg-gray-50' : ''}
              {...getFieldProps('sku')}
            />
            {isEdit && (
              <p className="mt-1 text-sm text-gray-500">
                El SKU no se puede modificar una vez creado el producto
              </p>
            )}
          </div>

          {formState.name?.value && (
            <Card className="bg-gray-50 p-4">
              <h4 className="font-medium text-gray-900 mb-2">Vista previa:</h4>
              <div className="text-sm space-y-1">
                <p><span className="font-medium">Nombre:</span> {formState.name.value}</p>
                {formState.description?.value && (
                  <p><span className="font-medium">Descripción:</span> {formState.description.value}</p>
                )}
                {formState.price?.value && (
                  <p><span className="font-medium">Precio:</span> ${parseFloat(formState.price.value).toFixed(2)}</p>
                )}
                {formState.stockQuantity?.value && (
                  <p><span className="font-medium">Stock:</span> {formState.stockQuantity.value} unidades</p>
                )}
                {formState.sku?.value && (
                  <p><span className="font-medium">SKU:</span> {formState.sku.value.toUpperCase()}</p>
                )}
              </div>
            </Card>
          )}

          <div className="flex gap-3 pt-6 border-t border-gray-200">
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              isLoading={isSubmitting}
              disabled={isSubmitting}
            >
              {isEdit ? 'Actualizar Producto' : 'Crear Producto'}
            </Button>

            <Button
              type="button"
              variant="secondary"
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </div>
    </Card>
  );
}