import { DashboardLayout } from '../components/common/DashboardLayout';
import { ProductList } from '../components/products/ProductList';

export function ProductsPage() {
  return (
    <DashboardLayout>
      <ProductList />
    </DashboardLayout>
  );
}