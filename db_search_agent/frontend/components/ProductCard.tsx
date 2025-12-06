import Image from "next/image";
import Link from "next/link";
import { Product } from "@/lib/types";

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <Link href={`/products/${product.slug}`}>
      <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
        {product.image && (
          <div className="relative h-64 w-full">
            <Image
              src={product.image}
              alt={product.name}
              fill
              className="object-cover"
            />
          </div>
        )}
        <div className="p-4">
          <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
          {product.brand && (
            <p className="text-sm text-gray-600 mb-2">{product.brand}</p>
          )}
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xl font-bold">${product.price}</span>
              {product.compareAtPrice && (
                <span className="text-sm text-gray-500 line-through ml-2">
                  ${product.compareAtPrice}
                </span>
              )}
            </div>
            {product.inStock ? (
              <span className="text-green-600 text-sm">In Stock</span>
            ) : (
              <span className="text-red-600 text-sm">Out of Stock</span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}

