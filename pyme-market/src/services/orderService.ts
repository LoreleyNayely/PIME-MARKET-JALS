import { ordersApiClient } from './apiClient';
import type { Cart } from '../interfaces/products';

interface Purchase {
  purchaseId: string;
  cartId: string;
  purchaseNumber: string;
  userId: string;
  totalAmount: number;
  taxAmount: number;
  discountAmount: number;
  finalAmount: number;
  paymentMethod: 'cash' | 'card' | 'transfer';
  status: 'pending' | 'completed' | 'cancelled';
  purchasedAt: string;
}

interface PurchaseCreate {
  cartId: string;
  userId: string;
  totalAmount: number;
  taxAmount: number;
  discountAmount?: number;
  paymentMethod: 'cash' | 'card' | 'transfer';
}

interface ReceiptData {
  purchaseNumber: string;
  userId: string;
  purchaseDate: string;
  totalAmount: number;
  taxAmount: number;
  discountAmount: number;
  finalAmount: number;
  paymentMethod: string;
  items: Array<{
    productName: string;
    quantity: number;
    unitPrice: number;
    subtotal: number;
  }>;
  summary: {
    subtotal: number;
    tax: number;
    discount: number;
    total: number;
  };
}

interface Receipt {
  receiptId: string;
  purchaseId: string;
  receiptData: ReceiptData;
  generatedAt: string;
}

export interface UserPurchase extends Purchase {
  receiptId?: string;
  receiptData?: ReceiptData;
}

export const orderService = {
  async createPurchase(data: PurchaseCreate): Promise<Purchase> {
    const response = await ordersApiClient.post<Purchase>('/purchases', data);
    return response;
  },

  async createPurchaseFromCart(
    cart: Cart, 
    userId: string, 
    cartId: string,
    paymentMethod: 'cash' | 'card' | 'transfer' = 'card'
  ): Promise<Purchase> {
    const totalAmount = cart.totalPrice;
    const taxAmount = totalAmount * 0.19;

    const purchaseData: PurchaseCreate = {
      cartId,
      userId,
      totalAmount,
      taxAmount,
      paymentMethod
    };

    const purchase = await this.createPurchase(purchaseData);
    
    try {
      await ordersApiClient.get(`/receipts/purchase/${purchase.purchaseId}/get-or-generate`);
    } catch (error) {
      console.error('Error getting or generating receipt:', error);
    }

    return purchase;
  },

  async getPurchase(purchaseId: string): Promise<Purchase> {
    const response = await ordersApiClient.get<Purchase>(`/purchases/${purchaseId}`);
    return response;
  },

  async getPurchaseSummary(purchaseId: string): Promise<any> {
    const response = await ordersApiClient.get(`/purchases/${purchaseId}/summary`);
    return response;
  },

  async generateReceipt(purchaseId: string): Promise<Receipt> {
    const response = await ordersApiClient.post<Receipt>(`/receipts/purchase/${purchaseId}`);
    return response;
  },

  async getReceipt(purchaseId: string): Promise<Receipt> {
    const response = await ordersApiClient.get<Receipt>(`/receipts/purchase/${purchaseId}`);
    return response;
  },

  async getFormattedReceipt(purchaseId: string): Promise<string> {
    try {
      const receipt = await this.getReceipt(purchaseId);
      const { receiptData } = receipt;
      
      if (!receiptData) {
        throw new Error('No se encontraron datos del recibo');
      }

      const formattedDate = new Date(receiptData.purchaseDate).toLocaleString('es-ES');
      
      let receiptText = `
===========================================
            PYME MARKET - RECIBO
===========================================
Número de Compra: ${receiptData.purchaseNumber || 'N/A'}
Fecha: ${formattedDate}
-------------------------------------------

PRODUCTOS:
`;

      if (Array.isArray(receiptData.items) && receiptData.items.length > 0) {
        receiptData.items.forEach(item => {
          if (item && typeof item === 'object') {
            const quantity = item.quantity || 0;
            const unitPrice = item.unitPrice || 0;
            const subtotal = item.subtotal || (quantity * unitPrice);
            
            receiptText += `
${item.productName || 'Producto sin nombre'}
  ${quantity} x $${unitPrice.toFixed(2)} = $${subtotal.toFixed(2)}
`;
          }
        });
      } else {
        receiptText += '\nNo hay productos en el recibo\n';
      }

      const summary = receiptData.summary || {
        subtotal: 0,
        tax: 0,
        discount: 0,
        total: 0
      };

      receiptText += `
-------------------------------------------
RESUMEN:
Subtotal:         $${(summary.subtotal || 0).toFixed(2)}
IVA (19%):        $${(summary.tax || 0).toFixed(2)}`;

      if (summary.discount && summary.discount > 0) {
        receiptText += `
Descuento:        $${summary.discount.toFixed(2)}`;
      }

      receiptText += `
-------------------------------------------
TOTAL:            $${(summary.total || 0).toFixed(2)}

Método de pago: ${(receiptData.paymentMethod || 'No especificado').toUpperCase()}
===========================================

¡Gracias por tu compra!
Tu satisfacción es nuestra prioridad.

ID de Compra: ${receipt.purchaseId}
===========================================`;

      return receiptText;
    } catch (error) {
      console.error('Error formatting receipt:', error);
      throw error;
    }
  },

  async getUserPurchases(userId: string): Promise<UserPurchase[]> {
    const response = await ordersApiClient.get<{ purchases: Purchase[], total: number }>(`/purchases/user/${userId}`);
    
    const purchasesWithReceipts = await Promise.all(
      response.purchases.map(async (purchase) => {
        try {
          const receipt = await this.getReceipt(purchase.purchaseId);
          return {
            ...purchase,
            receiptId: receipt.receiptId,
            receiptData: receipt.receiptData
          };
        } catch (error) {
          return purchase;
        }
      })
    );

    return purchasesWithReceipts;
  },
};