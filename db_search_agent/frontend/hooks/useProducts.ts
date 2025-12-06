"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { Product, ProductSearchResult } from "@/lib/types";

interface UseProductsOptions {
  initialFilters?: {
    q?: string;
    category?: string;
    minPrice?: number;
    maxPrice?: number;
    brand?: string;
    inStock?: boolean;
    featured?: boolean;
  };
  autoLoad?: boolean;
}

export function useProducts(options: UseProductsOptions = {}) {
  const { initialFilters = {}, autoLoad = false } = options;

  const [filters, setFilters] = useState(initialFilters);
  const [results, setResults] = useState<ProductSearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.products.search({
        ...filters,
        limit: 20,
        offset: 0,
      });
      setResults(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to search products";
      setError(errorMessage);
      console.error("Product search error:", err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    if (autoLoad) {
      searchProducts();
    }
  }, [autoLoad, searchProducts]);

  const updateFilters = useCallback((newFilters: Partial<typeof filters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(initialFilters);
  }, [initialFilters]);

  return {
    products: results?.products || [],
    total: results?.total || 0,
    loading,
    error,
    filters,
    updateFilters,
    resetFilters,
    searchProducts,
  };
}

export function useProduct(slug: string) {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProduct = async () => {
      if (!slug) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const data = await api.products.getBySlug(slug);
        setProduct(data);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load product";
        setError(errorMessage);
        console.error("Product fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [slug]);

  return { product, loading, error };
}

