import { useAuth } from '../hooks/useAuth';
import { DashboardLayout } from '../components/common/DashboardLayout';
import { Card } from '../components/ui/Card';
import {
  ShoppingBagIcon,
  ShoppingCartIcon,
  UserGroupIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  color: 'blue' | 'green' | 'purple' | 'orange';
}

function StatCard({ title, value, icon: Icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-semibold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </Card>
  );
}

export function HomePage() {
  const { user, isAdmin } = useAuth();

  const adminStats = [
    {
      title: 'Total Productos',
      value: 124,
      icon: ShoppingBagIcon,
      color: 'blue' as const,
    },
    {
      title: 'Órdenes Hoy',
      value: 18,
      icon: ShoppingCartIcon,
      color: 'green' as const,
    },
    {
      title: 'Clientes Activos',
      value: 67,
      icon: UserGroupIcon,
      color: 'purple' as const,
    },
    {
      title: 'Ventas del Mes',
      value: '$12,345',
      icon: CurrencyDollarIcon,
      color: 'orange' as const,
    },
  ];

  const clientStats = [
    {
      title: 'Mi Carrito',
      value: 3,
      icon: ShoppingCartIcon,
      color: 'blue' as const,
    },
    {
      title: 'Mis Órdenes',
      value: 12,
      icon: ShoppingBagIcon,
      color: 'green' as const,
    },
    {
      title: 'Favoritos',
      value: 8,
      icon: ShoppingBagIcon,
      color: 'purple' as const,
    },
    {
      title: 'Total Gastado',
      value: '$2,345',
      icon: CurrencyDollarIcon,
      color: 'orange' as const,
    },
  ];

  const stats = isAdmin() ? adminStats : clientStats;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="border-b border-gray-200 pb-4">
          <h1 className="text-2xl font-bold text-gray-900">
            ¡Bienvenido{isAdmin() ? ' Administrador' : ''}, {user?.name}! 👋
          </h1>
          <p className="mt-2 text-gray-600">
            {isAdmin()
              ? 'Gestiona tu marketplace desde este panel de control'
              : 'Explora nuestros productos y gestiona tus compras'
            }
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <StatCard
              key={index}
              title={stat.title}
              value={stat.value}
              icon={stat.icon}
              color={stat.color}
            />
          ))}
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {isAdmin() ? 'Acciones de Administrador' : 'Acciones Rápidas'}
            </h3>
            <div className="space-y-3">
              {isAdmin() ? (
                <>
                  <a
                    href="/dashboard/products"
                    className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                  >
                    <ShoppingBagIcon className="h-5 w-5 text-blue-600" />
                    <span className="font-medium">Gestionar Productos</span>
                  </a>
                  <a
                    href="/dashboard/orders"
                    className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                  >
                    <ShoppingCartIcon className="h-5 w-5 text-green-600" />
                    <span className="font-medium">Ver Todas las Órdenes</span>
                  </a>
                </>
              ) : (
                <>
                  <a
                    href="/dashboard/catalog"
                    className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                  >
                    <ShoppingBagIcon className="h-5 w-5 text-blue-600" />
                    <span className="font-medium">Explorar Catálogo</span>
                  </a>
                  <a
                    href="/dashboard/cart"
                    className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                  >
                    <ShoppingCartIcon className="h-5 w-5 text-green-600" />
                    <span className="font-medium">Ver Mi Carrito</span>
                  </a>
                </>
              )}
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Actividad Reciente
            </h3>
            <div className="space-y-3">
              {isAdmin() ? (
                <>
                  <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-gray-600">Nueva orden #1234 recibida</span>
                    <span className="text-gray-400 ml-auto">hace 5 min</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-gray-600">Producto actualizado: Laptop HP</span>
                    <span className="text-gray-400 ml-auto">hace 1 hora</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span className="text-gray-600">Nuevo cliente registrado</span>
                    <span className="text-gray-400 ml-auto">hace 2 horas</span>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-gray-600">Producto agregado al carrito</span>
                    <span className="text-gray-400 ml-auto">hace 10 min</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-gray-600">Orden #1230 entregada</span>
                    <span className="text-gray-400 ml-auto">hace 2 días</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span className="text-gray-600">Nuevo mensaje en chat</span>
                    <span className="text-gray-400 ml-auto">hace 1 semana</span>
                  </div>
                </>
              )}
            </div>
          </Card>
        </div>

        <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <div className="flex items-start gap-4">
            <div className="flex-1">
              <h3 className="text-lg font-medium text-blue-900 mb-2">
                {isAdmin() ? '🚀 Panel de Administrador' : '🛍️ ¡Comienza a comprar!'}
              </h3>
              <p className="text-blue-700 mb-4">
                {isAdmin()
                  ? 'Desde aquí puedes gestionar todos los aspectos de tu marketplace: productos, órdenes, clientes y más.'
                  : 'Explora nuestro catálogo de productos, agrega artículos a tu carrito y realiza compras de manera segura.'
                }
              </p>
              <div className="flex gap-3">
                <a
                  href={isAdmin() ? "/dashboard/products" : "/dashboard/catalog"}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {isAdmin() ? 'Gestionar Productos' : 'Ver Catálogo'}
                </a>
                <a
                  href="/dashboard/chat"
                  className="inline-flex items-center px-4 py-2 bg-white text-blue-600 text-sm font-medium rounded-lg border border-blue-600 hover:bg-blue-50 transition-colors"
                >
                  Abrir Chat
                </a>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
}
