import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { CartProvider } from './hooks/useCart';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { ForgotPasswordPage } from './pages/auth/ForgotPasswordPage';
import { ChangePasswordPage } from './pages/auth/ChangePasswordPage';
import { HomePage } from './pages/HomePage';
import { LandingPage } from './pages/LandingPage';
import { ProductsPage } from './pages/ProductsPage';
import { CreateProductPage } from './pages/CreateProductPage';
import { EditProductPage } from './pages/EditProductPage';
import { ProductDetailPage } from './pages/ProductDetailPage';
import { CatalogPage } from './pages/CatalogPage';
import { CartPage } from './pages/CartPage';
import { OrdersPage } from './pages/OrdersPage';
import { ChatPage } from './pages/ChatPage';
import { Toaster } from 'react-hot-toast';

export function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <Toaster position="top-right" />
          <Routes>
            <Route path="/" element={<LandingPage />} />

            <Route path="/auth/login" element={<LoginPage />} />
            <Route path="/auth/register" element={<RegisterPage />} />
            <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />

            <Route
              path="/auth/change-password"
              element={
                <ProtectedRoute>
                  <ChangePasswordPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <HomePage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard/products/:productId"
              element={
                <ProtectedRoute>
                  <ProductDetailPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard/products"
              element={
                <ProtectedRoute requireAdmin>
                  <ProductsPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard/products/new"
              element={
                <ProtectedRoute requireAdmin>
                  <CreateProductPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard/products/:productId/edit"
              element={
                <ProtectedRoute requireAdmin>
                  <EditProductPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard/catalog"
              element={
                <ProtectedRoute>
                  <CatalogPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard/cart"
              element={
                <ProtectedRoute>
                  <CartPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard/orders"
              element={
                <ProtectedRoute>
                  <OrdersPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard/chat"
              element={
                <ProtectedRoute>
                  <ChatPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard/profile"
              element={
                <ProtectedRoute>
                  <div className="p-8 text-center">
                    <h2 className="text-2xl font-bold text-gray-900">Mi Perfil</h2>
                    <p className="text-gray-600 mt-2">Próximamente</p>
                  </div>
                </ProtectedRoute>
              }
            />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}
