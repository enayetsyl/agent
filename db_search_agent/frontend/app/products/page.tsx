"use client";

import { useState } from "react";
import { useProducts } from "@/hooks/useProducts";
import ProductList from "@/components/ProductList";
import CategoryFilter from "@/components/CategoryFilter";
import PriceFilter from "@/components/PriceFilter";

export default function ProductsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [category, setCategory] = useState<string | undefined>();
  const [minPrice, setMinPrice] = useState<number | undefined>();
  const [maxPrice, setMaxPrice] = useState<number | undefined>();
  const [inStock, setInStock] = useState(false);

  const {
    products,
    total,
    loading,
    error,
    updateFilters,
    searchProducts,
  } = useProducts();

  const handleSearch = () => {
    updateFilters({
      q: searchQuery || undefined,
      category,
      minPrice,
      maxPrice,
      inStock: inStock || undefined,
    });
    searchProducts();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Products</h1>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search products..."
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <CategoryFilter
              selectedCategory={category}
              onCategoryChange={setCategory}
            />
            <PriceFilter
              minPrice={minPrice}
              maxPrice={maxPrice}
              onMinPriceChange={setMinPrice}
              onMaxPriceChange={setMaxPrice}
            />
            <div className="flex items-center">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={inStock}
                  onChange={(e) => setInStock(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm font-medium text-gray-700">
                  In Stock Only
                </span>
              </label>
            </div>
          </div>

          <button
            onClick={handleSearch}
            disabled={loading}
            className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Results */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-12">
            <p className="text-gray-500">Loading products...</p>
          </div>
        )}

        {!loading && !error && (
          <>
            {total > 0 && (
              <p className="text-gray-600 mb-4">
                Found {total} product{total !== 1 ? "s" : ""}
              </p>
            )}
            <ProductList products={products} />
          </>
        )}
      </div>
    </div>
  );
}

