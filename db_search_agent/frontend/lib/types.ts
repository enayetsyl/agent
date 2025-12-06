export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  shortDescription: string;
  price: number;
  compareAtPrice?: number;
  category?: Category;
  brand?: string;
  image?: string;
  images: ProductImage[];
  variants: ProductVariant[];
  tags: ProductTag[];
  averageRating?: number;
  reviewCount: number;
  inStock: boolean;
}

export interface ProductVariant {
  id: number;
  name: string;
  sku?: string;
  price?: number;
  stockQuantity: number;
  attributes: Record<string, string>;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
}

export interface ProductImage {
  url: string;
  altText?: string;
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

