"use client";

import { use } from "react";
import { useProduct } from "@/hooks/useProducts";
import ProductDetails from "@/components/ProductDetails";

interface ProductPageProps {
  params: Promise<{ slug: string }>;
}

export default function ProductPage({ params }: ProductPageProps) {
  const { slug } = use(params);
  return <ProductPageClient slug={slug} />;
}

function ProductPageClient({ slug }: { slug: string }) {
  const { product, loading, error } = useProduct(slug);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500 text-lg">Loading product...</p>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg mb-2">Product not found</p>
          <p className="text-gray-500">{error || "The product you're looking for doesn't exist."}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <ProductDetails product={product} />
    </div>
  );
}

