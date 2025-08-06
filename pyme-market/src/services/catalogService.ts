import type { 
  CatalogProduct, 
  CatalogResponse, 
  CatalogFilters 
} from '../interfaces/products';
import { productService } from './productService';
import { config, devLog } from '../config/app';

class CatalogService {
  private transformToCatalogProduct(product: any): CatalogProduct {
    return {
      productId: product.productId,
      name: product.name,
      description: product.description || '',
      price: product.price,
      stockQuantity: product.stockQuantity,
      sku: product.sku,
      imageUrl: product.imageUrl,
      category: product.category || 'General',
      isAvailable: product.isActive && product.stockQuantity > 0,
      rating: Math.random() * 2 + 3,
      reviewsCount: Math.floor(Math.random() * 100) + 1,
    };
  }

  async getCatalogProducts(filters: CatalogFilters = {}): Promise<CatalogResponse> {
    try {
      devLog('🛍️ Obteniendo productos del catálogo', filters);

      const productFilters = {
        search: filters.search,
        minPrice: filters.minPrice,
        maxPrice: filters.maxPrice,
        includeInactive: false,
      };

      const response = await productService.getAllProducts(productFilters);
      
      let catalogProducts = response.products
        .filter(product => product.isActive && product.stockQuantity > 0)
        .map(product => this.transformToCatalogProduct(product));

      if (filters.inStock !== undefined) {
        catalogProducts = catalogProducts.filter(product => 
          filters.inStock ? product.stockQuantity > 0 : true
        );
      }

      if (filters.category && filters.category !== 'all') {
        catalogProducts = catalogProducts.filter(product => 
          product.category === filters.category
        );
      }

      if (filters.sortBy) {
        catalogProducts.sort((a, b) => {
          const order = filters.sortOrder === 'desc' ? -1 : 1;
          
          switch (filters.sortBy) {
            case 'name':
              return order * a.name.localeCompare(b.name);
            case 'price':
              return order * (a.price - b.price);
            case 'newest':
              return order * a.productId.localeCompare(b.productId);
            case 'popular':
              return order * ((b.reviewsCount || 0) - (a.reviewsCount || 0));
            default:
              return 0;
          }
        });
      }

      devLog('✅ Productos del catálogo obtenidos', { count: catalogProducts.length });

      return {
        products: catalogProducts,
        total: catalogProducts.length,
        page: 1,
        limit: catalogProducts.length,
        hasMore: false,
      };

    } catch (error) {
      devLog('❌ Error obteniendo productos del catálogo', error);
      throw error;
    }
  }

  async getCatalogProduct(productId: string): Promise<CatalogProduct> {
    try {
      devLog('🔍 Obteniendo producto del catálogo', { productId });

      const product = await productService.getProduct(productId);
      
      if (!product.isActive || product.stockQuantity <= 0) {
        throw new Error('Producto no disponible');
      }

      const catalogProduct = this.transformToCatalogProduct(product);
      
      devLog('✅ Producto del catálogo obtenido', catalogProduct);
      return catalogProduct;

    } catch (error) {
      devLog('❌ Error obteniendo producto del catálogo', error);
      throw error;
    }
  }

  async getCategories(): Promise<string[]> {
    try {
      devLog('📂 Obteniendo categorías del catálogo');

      const response = await productService.getAllProducts({ includeInactive: false });
      const categories = [...new Set(
        response.products
          .filter(product => product.isActive)
          .map(product => product.category || 'General')
      )];

      devLog('✅ Categorías obtenidas', categories);
      return categories.sort();

    } catch (error) {
      devLog('❌ Error obteniendo categorías', error);
      throw error;
    }
  }

  async searchProducts(query: string, limit: number = 10): Promise<CatalogProduct[]> {
    try {
      if (!query.trim()) return [];

      devLog('🔍 Buscando productos', { query, limit });

      const response = await productService.getAllProducts({ 
        search: query,
        includeInactive: false 
      });
      
      const products = response.products
        .filter(product => product.isActive && product.stockQuantity > 0)
        .slice(0, limit)
        .map(product => this.transformToCatalogProduct(product));

      devLog('✅ Búsqueda completada', { found: products.length });
      return products;

    } catch (error) {
      devLog('❌ Error en búsqueda de productos', error);
      throw error;
    }
  }

  async checkProductAvailability(productId: string, quantity: number): Promise<boolean> {
    try {
      const product = await productService.getProduct(productId);
      return product.isActive && product.stockQuantity >= quantity;
    } catch (error) {
      devLog('❌ Error verificando disponibilidad', error);
      return false;
    }
  }
}

export const catalogService = new CatalogService();