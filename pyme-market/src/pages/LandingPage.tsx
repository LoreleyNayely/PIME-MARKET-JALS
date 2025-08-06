import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">
                PYME Market
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              <Link to="/auth/login">
                <Button variant="ghost" size="md">
                  Iniciar sesión
                </Button>
              </Link>
              <Link to="/auth/register">
                <Button variant="primary" size="md">
                  Registrarse
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            Tu marketplace para{' '}
            <span className="text-blue-600">pequeñas empresas</span>
          </h1>

          <p className="text-xl sm:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Conecta, vende y crece. PYME Market es la plataforma diseñada
            especialmente para pequeñas y medianas empresas.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link to="/auth/register">
              <Button variant="primary" size="lg" className="w-full sm:w-auto">
                Empezar gratis
              </Button>
            </Link>
            <Link to="/auth/login">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Ya tengo cuenta
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
              <CardTitle>Vende fácilmente</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Configura tu tienda en minutos y empieza a vender tus productos
                a miles de clientes potenciales.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <CardTitle>Gestiona tu negocio</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Dashboard completo para administrar productos, pedidos,
                inventario y estadísticas de ventas.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
              <CardTitle>Conecta con clientes</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Construye relaciones duraderas con tus clientes y
                expande tu red de contactos comerciales.
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-16 bg-white rounded-2xl p-8 shadow-lg">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            ¿Listo para hacer crecer tu negocio?
          </h2>
          <p className="text-lg text-gray-600 mb-6">
            Únete a cientos de pequeñas empresas que ya están vendiendo en PYME Market
          </p>
          <Link to="/auth/register">
            <Button variant="primary" size="lg">
              Crear cuenta gratis
            </Button>
          </Link>
        </div>
      </main>

      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-lg font-semibold mb-2">PYME Market</h3>
            <p className="text-gray-400">
              © 2025 PYME Market. Tu plataforma de confianza para pequeñas empresas.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
