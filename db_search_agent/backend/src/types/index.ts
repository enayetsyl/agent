// Product-related types
export interface ProductSearchFilters {
  query?: string;
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  brand?: string;
  inStock?: boolean;
  featured?: boolean;
  tags?: string[];
  limit?: number;
  offset?: number;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  shortDescription: string | null;
  price: number;
  compareAtPrice?: number | null;
  category?: Category | null;
  brand?: string | null;
  image?: string | null;
  images: ProductImage[];
  variants: ProductVariant[];
  tags: ProductTag[];
  averageRating?: number | null;
  reviewCount: number;
  inStock: boolean;
}

export interface ProductVariant {
  id: number;
  name: string;
  sku?: string | null;
  price?: number | null;
  stockQuantity: number;
  attributes: Record<string, string>;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  parentId?: number | null;
  children?: Category[];
}

export interface ProductImage {
  url: string;
  altText?: string | null;
  isPrimary: boolean;
}

export interface ProductTag {
  id: number;
  name: string;
  slug: string;
}

export interface ProductSearchResult {
  products: Product[];
  total: number;
  limit: number;
  offset: number;
}

export interface ProductAvailability {
  available: boolean;
  message?: string;
  variants?: Array<{
    id: number;
    name: string;
    stockQuantity: number;
    price: number | null;
    attributes: Record<string, string>;
  }>;
  totalStock?: number;
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ApiError {
  error: string;
  message: string;
  details?: any;
}

// Agent-related types
export interface AgentQueryRequest {
  message: string;
  sessionId?: string;
}

export interface AgentQueryResponse {
  response: string;
}
