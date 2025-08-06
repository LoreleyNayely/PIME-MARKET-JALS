import { ordersApiClient } from './apiClient';
import type { Cart } from '../interfaces/products';

interface ServerCart {
  cartId: string;
  userId: string;
  status: 'active' | 'completed' | 'abandoned';
  totalAmount: number;
  createdAt: string;
  updatedAt: string;
}

interface CartItemCreate {
  productId: string;
  productName: string;
  productSku: string;
  unitPrice: number;
  quantity: number;
}

export const cartService = {
  async createCart(userId: string): Promise<ServerCart> {
    const response = await ordersApiClient.post<ServerCart>('/carts', {
      userId,
    });
    return response;
  },

  async syncCartWithServer(cart: Cart, cartId: string): Promise<ServerCart> {
    await ordersApiClient.delete(`/cart-items/cart/${cartId}/clear`);

    for (const item of cart.items) {
      const itemData: CartItemCreate = {
        productId: item.productId,
        productName: item.product.name,
        productSku: item.product.sku,
        unitPrice: item.product.price,
        quantity: item.quantity
      };
      await ordersApiClient.post(`/cart-items/${cartId}/items`, itemData);
    }

    const response = await ordersApiClient.get<ServerCart>(`/carts/${cartId}`);
    return response;
  },

  async getActiveCart(userId: string): Promise<ServerCart | null> {
    try {
      const response = await ordersApiClient.get<ServerCart>(`/carts/user/${userId}/active`);
      return response;
    } catch (error) {
      if ((error as any)?.status === 404) {
        return null;
      }
      throw error;
    }
  }
};