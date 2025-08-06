export interface Product {
  productId: string;
  name: string;
  description?: string;
  price: number;
  stockQuantity: number;
  sku: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ProductCreate {
  name: string;
  description?: string;
  price: number;
  stockQuantity: number;
  sku: string;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  price?: number;
  stockQuantity?: number;
  sku?: string;
  isActive?: boolean;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
}

export interface StockCheckResponse {
  productId: string;
  sku: string;
  currentStock: number;
  requiredQuantity: number;
  isAvailable: boolean;
  availableQuantity: number;
}

export interface ProductFilters {
  includeInactive?: boolean;
  search?: string;
  minPrice?: number;
  maxPrice?: number;
  minStock?: number;
  maxStock?: number;
}

export interface CartItem {
  productId: string;
  product: CatalogProduct;
  quantity: number;
  addedAt: Date;
}

export interface Cart {
  items: CartItem[];
  totalItems: number;
  totalPrice: number;
  updatedAt: Date;
}

export interface CartSummary {
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  itemsCount: number;
}

export interface CatalogFilters {
  search?: string;
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  sortBy?: 'name' | 'price' | 'newest' | 'popular';
  sortOrder?: 'asc' | 'desc';
  inStock?: boolean;
}

export interface CatalogProduct {
  productId: string;
  name: string;
  description: string;
  price: number;
  stockQuantity: number;
  sku: string;
  imageUrl?: string;
  category?: string;
  isAvailable: boolean;
  rating?: number;
  reviewsCount?: number;
}

export interface CatalogResponse {
  products: CatalogProduct[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export type CartAction =
  | { type: 'ADD_ITEM'; payload: { product: CatalogProduct; quantity: number } }
  | { type: 'REMOVE_ITEM'; payload: { productId: string } }
  | { type: 'UPDATE_QUANTITY'; payload: { productId: string; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'LOAD_CART'; payload: Cart };