import { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import type { Cart, CartItem, CartAction, CatalogProduct, CartSummary } from '../interfaces/products';
import toast from 'react-hot-toast';

const initialCart: Cart = {
  items: [],
  totalItems: 0,
  totalPrice: 0,
  updatedAt: new Date(),
};

function cartReducer(state: Cart, action: CartAction): Cart {
  switch (action.type) {
    case 'ADD_ITEM': {
      const { product, quantity } = action.payload;
      const existingItemIndex = state.items.findIndex(item => item.productId === product.productId);

      let newItems: CartItem[];

      if (existingItemIndex >= 0) {
        newItems = state.items.map((item, index) =>
          index === existingItemIndex
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        const newItem: CartItem = {
          productId: product.productId,
          product,
          quantity,
          addedAt: new Date(),
        };
        newItems = [...state.items, newItem];
      }

      const totalItems = newItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = newItems.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);

      return {
        items: newItems,
        totalItems,
        totalPrice,
        updatedAt: new Date(),
      };
    }

    case 'REMOVE_ITEM': {
      const newItems = state.items.filter(item => item.productId !== action.payload.productId);
      const totalItems = newItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = newItems.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);

      return {
        items: newItems,
        totalItems,
        totalPrice,
        updatedAt: new Date(),
      };
    }

    case 'UPDATE_QUANTITY': {
      const { productId, quantity } = action.payload;

      if (quantity <= 0) {
        return cartReducer(state, { type: 'REMOVE_ITEM', payload: { productId } });
      }

      const newItems = state.items.map(item =>
        item.productId === productId
          ? { ...item, quantity }
          : item
      );

      const totalItems = newItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = newItems.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);

      return {
        items: newItems,
        totalItems,
        totalPrice,
        updatedAt: new Date(),
      };
    }

    case 'CLEAR_CART': {
      return {
        ...initialCart,
        updatedAt: new Date(),
      };
    }

    case 'LOAD_CART': {
      return action.payload;
    }

    default:
      return state;
  }
}

interface CartContextType {
  cart: Cart;
  addToCart: (product: CatalogProduct, quantity?: number) => void;
  removeFromCart: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  getCartSummary: () => CartSummary;
  isInCart: (productId: string) => boolean;
  getItemQuantity: (productId: string) => number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

interface CartProviderProps {
  children: ReactNode;
}

export function CartProvider({ children }: CartProviderProps) {
  const [cart, dispatch] = useReducer(cartReducer, initialCart);

  useEffect(() => {
    const savedCart = localStorage.getItem('pyme_cart');
    if (savedCart) {
      try {
        const parsedCart = JSON.parse(savedCart);
        const cartWithDates = {
          ...parsedCart,
          updatedAt: new Date(parsedCart.updatedAt),
          items: parsedCart.items.map((item: any) => ({
            ...item,
            addedAt: new Date(item.addedAt),
            product: {
              ...item.product,
              createdAt: new Date(item.product.createdAt),
              updatedAt: new Date(item.product.updatedAt),
            }
          }))
        };
        dispatch({ type: 'LOAD_CART', payload: cartWithDates });
      } catch (error) {
        console.error('Error loading cart from localStorage:', error);
        toast.error('Error al cargar el carrito guardado');
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('pyme_cart', JSON.stringify(cart));
  }, [cart]);

  const addToCart = (product: CatalogProduct, quantity: number = 1) => {
    dispatch({
      type: 'ADD_ITEM',
      payload: { product, quantity }
    });
    toast.success(`${product.name} agregado al carrito`);
  };

  const removeFromCart = (productId: string) => {
    const item = cart.items.find(item => item.productId === productId);
    dispatch({
      type: 'REMOVE_ITEM',
      payload: { productId }
    });
    if (item) {
      toast.success(`${item.product.name} removido del carrito`);
    }
  };

  const updateQuantity = (productId: string, quantity: number) => {
    dispatch({
      type: 'UPDATE_QUANTITY',
      payload: { productId, quantity }
    });
  };

  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' });
    toast.success('Carrito vaciado');
  };

  const getCartSummary = (): CartSummary => {
    return {
      totalItems: cart.totalItems,
      totalPrice: cart.totalPrice,
      itemCount: cart.items.length,
    };
  };

  const isInCart = (productId: string): boolean => {
    return cart.items.some(item => item.productId === productId);
  };

  const getItemQuantity = (productId: string): number => {
    const item = cart.items.find(item => item.productId === productId);
    return item ? item.quantity : 0;
  };

  const value: CartContextType = {
    cart,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    getCartSummary,
    isInCart,
    getItemQuantity,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}