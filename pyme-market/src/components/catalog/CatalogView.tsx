import React, { useState, useEffect, useMemo } from 'react';
import { CatalogProduct, CatalogFilters } from '../../interfaces/products';
import { catalogService } from '../../services/catalogService';
import { useCart } from '../../hooks/useCart';
import { ProductCard } from './ProductCard';
import { CatalogFilters as CatalogFiltersComponent } from './CatalogFilters';
import { SearchBar } from '../common/SearchBar';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { ErrorMessage } from '../ui/ErrorMessage';

interface CatalogViewProps {
  className?: string;
}

export const CatalogView: React.FC<CatalogViewProps> = ({ className = '' }) => {
  const [products, setProducts] = useState<CatalogProduct[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<CatalogProduct[]>([]);
  const [filters, setFilters] = useState<CatalogFilters>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<string[]>([]);

  const { addToCart } = useCart();

  useEffect(() => {
    const loadCatalogData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [catalogProducts, availableCategories] = await Promise.all([
          catalogService.getCatalogProducts(),
          catalogService.getCategories()
        ]);

        setProducts(catalogProducts);
        setFilteredProducts(catalogProducts);
        setCategories(availableCategories);

      } catch (err) {
        console.error('Error cargando catálogo:', err);
        setError('Error al cargar el catálogo. Inténtalo de nuevo.');
      } finally {
        setLoading(false);
      }
    };

    loadCatalogData();
  }, []);

  const applyFiltersAndSearch = useMemo(() => {
    let result = [...products];

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(product =>
        product.name.toLowerCase().includes(query) ||
        product.description.toLowerCase().includes(query) ||
        (product.category?.toLowerCase().includes(query))
      );
    }

    if (filters.category) {
      result = result.filter(product => product.category === filters.category);
    }

    if (filters.minPrice !== undefined) {
      result = result.filter(product => product.price >= filters.minPrice!);
    }

    if (filters.maxPrice !== undefined) {
      result = result.filter(product => product.price <= filters.maxPrice!);
    }

    if (filters.availability === 'in-stock') {
      result = result.filter(product => product.stockQuantity > 0);
    } else if (filters.availability === 'out-of-stock') {
      result = result.filter(product => product.stockQuantity === 0);
    }

    if (filters.sortBy) {
      result.sort((a, b) => {
        switch (filters.sortBy) {
          case 'price-asc':
            return a.price - b.price;
          case 'price-desc':
            return b.price - a.price;
          case 'name-asc':
            return a.name.localeCompare(b.name);
          case 'name-desc':
            return b.name.localeCompare(a.name);
          case 'newest':
            return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
          default:
            return 0;
        }
      });
    }

    return result;
  }, [products, searchQuery, filters]);

  useEffect(() => {
    setFilteredProducts(applyFiltersAndSearch);
  }, [applyFiltersAndSearch]);

  const handleAddToCart = async (product: CatalogProduct, quantity: number = 1) => {
    try {
      const isAvailable = await catalogService.checkProductAvailability(product.id, quantity);

      if (!isAvailable) {
        setError('Producto no disponible o sin stock suficiente');
        return;
      }

      addToCart({
        id: product.id,
        name: product.name,
        price: product.price,
        imageUrl: product.imageUrl,
        maxQuantity: product.stockQuantity
      }, quantity);

    } catch (err) {
      console.error('Error agregando al carrito:', err);
      setError('Error al agregar el producto al carrito');
    }
  };

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
  };

  const handleFiltersChange = (newFilters: CatalogFilters) => {
    setFilters(newFilters);
  };

  const clearFilters = () => {
    setFilters({});
    setSearchQuery('');
  };

  if (loading) {
    return (
      <div className={`catalog-view ${className}`}>
        <LoadingSpinner message="Cargando catálogo..." />
      </div>
    );
  }

  return (
    <div className={`catalog-view ${className}`}>
      <div className="catalog-header">
        <h2 className="catalog-title">Catálogo de Productos</h2>
        <SearchBar
          placeholder="Buscar productos..."
          value={searchQuery}
          onChange={handleSearchChange}
          className="catalog-search"
        />
      </div>

      {error && (
        <ErrorMessage
          message={error}
          onDismiss={() => setError(null)}
          className="catalog-error"
        />
      )}

      <div className="catalog-content">
        <aside className="catalog-sidebar">
          <CatalogFiltersComponent
            filters={filters}
            categories={categories}
            onFiltersChange={handleFiltersChange}
            onClearFilters={clearFilters}
            productCount={filteredProducts.length}
          />
        </aside>

        <main className="catalog-main">
          {filteredProducts.length === 0 ? (
            <div className="no-products">
              <p>No se encontraron productos que coincidan con tu búsqueda.</p>
              {(searchQuery || Object.keys(filters).length > 0) && (
                <button
                  onClick={clearFilters}
                  className="btn btn-secondary"
                >
                  Limpiar filtros
                </button>
              )}
            </div>
          ) : (
            <>
              <div className="catalog-results-info">
                <span className="results-count">
                  {filteredProducts.length} producto{filteredProducts.length !== 1 ? 's' : ''} encontrado{filteredProducts.length !== 1 ? 's' : ''}
                </span>
              </div>

              <div className="products-grid">
                {filteredProducts.map(product => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onAddToCart={handleAddToCart}
                    className="catalog-product-card"
                  />
                ))}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
};