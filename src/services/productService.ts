import type { 
  Product, 
  ProductCreate, 
  ProductUpdate, 
  ProductListResponse,
  StockCheckResponse,
  ProductFilters 
} from '../interfaces/products';
import { productsApiClient } from './apiClient';
import { devLog } from '../config/app';

class ProductService {
  private readonly fallbackProducts: Product[] = [];

  constructor() {
    this.initializeFallbackProducts();
  }

  private initializeFallbackProducts(): void {
    const savedProducts = localStorage.getItem('demo_products');
    if (savedProducts) {
      this.fallbackProducts.push(...JSON.parse(savedProducts));
    } else {
      this.fallbackProducts.push(
        {
          productId: '1',
          name: 'Laptop Dell Inspiron 15',
          description: 'Laptop empresarial con procesador Intel Core i5, 8GB RAM, 256GB SSD',
          price: 1299.99,
          stockQuantity: 15,
          sku: 'DELL-INSP-15-001',
          isActive: true,
          createdAt: new Date('2024-01-15'),
          updatedAt: new Date('2024-01-15'),
        },
        {
          productId: '2',
          name: 'Mouse Logitech MX Master 3',
          description: 'Mouse inalámbrico ergonómico para productividad',
          price: 99.99,
          stockQuantity: 50,
          sku: 'LOG-MX-MASTER-3',
          isActive: true,
          createdAt: new Date('2024-01-16'),
          updatedAt: new Date('2024-01-16'),
        },
        {
          productId: '3',
          name: 'Monitor Samsung 27"',
          description: 'Monitor 4K UHD de 27 pulgadas ideal para oficina',
          price: 349.99,
          stockQuantity: 8,
          sku: 'SAM-MON-27-4K',
          isActive: true,
          createdAt: new Date('2024-01-17'),
          updatedAt: new Date('2024-01-17'),
        }
      );
      this.saveFallbackProducts();
    }
  }

  private saveFallbackProducts(): void {
    localStorage.setItem('demo_products', JSON.stringify(this.fallbackProducts));
  }

  private transformProduct(apiProduct: unknown): Product {
    const product = apiProduct as any;
    return {
      productId: product.productId || product.product_id,
      name: product.name,
      description: product.description,
      price: typeof product.price === 'string' ? parseFloat(product.price) : product.price,
      stockQuantity: product.stockQuantity || product.stock_quantity,
      sku: product.sku,
      isActive: product.isActive || product.is_active,
      createdAt: new Date(product.createdAt || product.created_at),
      updatedAt: new Date(product.updatedAt || product.updated_at),
    };
  }

  async getAllProducts(filters?: ProductFilters): Promise<ProductListResponse> {
    try {
      devLog('📦 Obteniendo productos del microservicio', filters);
      
      const params = new URLSearchParams();
      if (filters?.includeInactive) {
        params.append('include_inactive', 'true');
      }

      const response = await productsApiClient.get<ProductListResponse>(
        `/products/?${params.toString()}`
      );

      const transformedProducts = response.products.map(this.transformProduct);
      
      devLog('✅ Productos obtenidos del microservicio', transformedProducts);
      return {
        products: transformedProducts,
        total: response.total
      };

    } catch (error) {
      devLog('⚠️ Error con microservicio de productos, usando fallback', error);
      return this.getAllProductsFallback(filters);
    }
  }

  private async getAllProductsFallback(filters?: ProductFilters): Promise<ProductListResponse> {
    let products = [...this.fallbackProducts];

    if (!filters?.includeInactive) {
      products = products.filter(p => p.isActive);
    }

    if (filters?.search) {
      const search = filters.search.toLowerCase();
      products = products.filter(p => 
        p.name.toLowerCase().includes(search) ||
        p.sku.toLowerCase().includes(search) ||
        p.description?.toLowerCase().includes(search)
      );
    }

    if (filters?.minPrice !== undefined) {
      products = products.filter(p => p.price >= filters.minPrice!);
    }

    if (filters?.maxPrice !== undefined) {
      products = products.filter(p => p.price <= filters.maxPrice!);
    }

    return { products, total: products.length };
  }

  async getProductById(productId: string): Promise<Product> {
    try {
      devLog('🔍 Obteniendo producto por ID del microservicio', productId);
      
      const response = await productsApiClient.get<Product>(`/products/${productId}`);
      const product = this.transformProduct(response);
      
      devLog('✅ Producto obtenido del microservicio', product);
      return product;

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      
      const product = this.fallbackProducts.find(p => p.productId === productId);
      if (!product) {
        throw new Error('Producto no encontrado');
      }
      return product;
    }
  }

  async createProduct(productData: ProductCreate): Promise<Product> {
    try {
      devLog('➕ Creando producto en microservicio', productData);
      
      const response = await productsApiClient.post<Product>('/products/', productData);
      const product = this.transformProduct(response);
      
      devLog('✅ Producto creado en microservicio', product);
      return product;

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      return this.createProductFallback(productData);
    }
  }

  private createProductFallback(productData: ProductCreate): Product {
    const newProduct: Product = {
      productId: Date.now().toString(),
      ...productData,
      isActive: true,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.fallbackProducts.push(newProduct);
    this.saveFallbackProducts();
    return newProduct;
  }

  async updateProduct(productId: string, updateData: ProductUpdate): Promise<Product> {
    try {
      devLog('📝 Actualizando producto en microservicio', { productId, updateData });
      
      const response = await productsApiClient.put<Product>(`/products/${productId}`, updateData);
      const product = this.transformProduct(response);
      
      devLog('✅ Producto actualizado en microservicio', product);
      return product;

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      return this.updateProductFallback(productId, updateData);
    }
  }

  private updateProductFallback(productId: string, updateData: ProductUpdate): Product {
    const index = this.fallbackProducts.findIndex(p => p.productId === productId);
    if (index === -1) {
      throw new Error('Producto no encontrado');
    }

    this.fallbackProducts[index] = {
      ...this.fallbackProducts[index],
      ...updateData,
      updatedAt: new Date(),
    };

    this.saveFallbackProducts();
    return this.fallbackProducts[index];
  }

  async deleteProduct(productId: string): Promise<void> {
    try {
      devLog('🗑️ Eliminando producto en microservicio', productId);
      
      await productsApiClient.delete(`/products/${productId}`);
      
      devLog('✅ Producto eliminado del microservicio');

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      this.deleteProductFallback(productId);
    }
  }

  private deleteProductFallback(productId: string): void {
    const index = this.fallbackProducts.findIndex(p => p.productId === productId);
    if (index === -1) {
      throw new Error('Producto no encontrado');
    }

    this.fallbackProducts[index].isActive = false;
    this.fallbackProducts[index].updatedAt = new Date();
    this.saveFallbackProducts();
  }

  async restoreProduct(productId: string): Promise<Product> {
    try {
      devLog('🔄 Restaurando producto en microservicio', productId);
      
      const response = await productsApiClient.patch<Product>(`/products/${productId}/restore`);
      const product = this.transformProduct(response);
      
      devLog('✅ Producto restaurado en microservicio', product);
      return product;

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      return this.restoreProductFallback(productId);
    }
  }

  private restoreProductFallback(productId: string): Product {
    const index = this.fallbackProducts.findIndex(p => p.productId === productId);
    if (index === -1) {
      throw new Error('Producto no encontrado');
    }

    this.fallbackProducts[index].isActive = true;
    this.fallbackProducts[index].updatedAt = new Date();
    this.saveFallbackProducts();
    
    return this.fallbackProducts[index];
  }

  async updateStock(productId: string, newStock: number): Promise<Product> {
    try {
      devLog('📊 Actualizando stock en microservicio', { productId, newStock });
      
      const response = await productsApiClient.patch<Product>(
        `/products/${productId}/stock?new_stock=${newStock}`
      );
      const product = this.transformProduct(response);
      
      devLog('✅ Stock actualizado en microservicio', product);
      return product;

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      return this.updateStockFallback(productId, newStock);
    }
  }

  private updateStockFallback(productId: string, newStock: number): Product {
    const index = this.fallbackProducts.findIndex(p => p.productId === productId);
    if (index === -1) {
      throw new Error('Producto no encontrado');
    }

    this.fallbackProducts[index].stockQuantity = newStock;
    this.fallbackProducts[index].updatedAt = new Date();
    this.saveFallbackProducts();
    
    return this.fallbackProducts[index];
  }

  async checkStockAvailability(productId: string, requiredQuantity: number): Promise<StockCheckResponse> {
    try {
      devLog('🔍 Verificando disponibilidad de stock', { productId, requiredQuantity });
      
      const response = await productsApiClient.get<StockCheckResponse>(
        `/products/${productId}/stock/check?required_quantity=${requiredQuantity}`
      );
      
      devLog('✅ Disponibilidad verificada', response);
      return response;

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      
      const product = this.fallbackProducts.find(p => p.productId === productId);
      if (!product) {
        throw new Error('Producto no encontrado');
      }

      return {
        productId,
        sku: product.sku,
        currentStock: product.stockQuantity,
        requiredQuantity,
        isAvailable: product.stockQuantity >= requiredQuantity,
        availableQuantity: product.stockQuantity,
      };
    }
  }
}

export const productService = new ProductService();