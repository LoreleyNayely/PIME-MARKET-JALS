import { DashboardLayout } from '../components/common/DashboardLayout';
import { ProductForm } from '../components/products/ProductForm';

export function CreateProductPage() {
  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <ProductForm />
      </div>
    </DashboardLayout>
  );
}