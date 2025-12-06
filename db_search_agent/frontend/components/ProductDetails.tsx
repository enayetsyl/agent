"use client";

import Image from "next/image";
import { Product } from "@/lib/types";
import { useState } from "react";

interface ProductDetailsProps {
  product: Product;
}

export default function ProductDetails({ product }: ProductDetailsProps) {
  const [selectedVariant, setSelectedVariant] = useState<Product["variants"][0] | null>(
    product.variants[0] || null
  );
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  const displayPrice = selectedVariant?.price || product.price;
  const displayImage = product.images[selectedImageIndex]?.url || product.image || "";

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Image Gallery */}
        <div>
          {displayImage && (
            <div className="relative aspect-square w-full mb-4">
              <Image
                src={displayImage}
                alt={product.name}
                fill
                className="object-cover rounded-lg"
                priority
              />
            </div>
          )}
          {product.images.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {product.images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImageIndex(index)}
                  className={`relative aspect-square rounded-lg overflow-hidden border-2 ${
                    selectedImageIndex === index
                      ? "border-blue-600"
                      : "border-gray-200"
                  }`}
                >
                  <Image
                    src={image.url}
                    alt={image.altText || product.name}
                    fill
                    className="object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div>
          <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
          {product.brand && (
            <p className="text-lg text-gray-600 mb-4">{product.brand}</p>
          )}
          
          {product.category && (
            <p className="text-sm text-gray-500 mb-4">
              Category: {product.category.name}
            </p>
          )}

          <div className="mb-6">
            <div className="flex items-center gap-4 mb-4">
              <span className="text-3xl font-bold">${displayPrice}</span>
              {product.compareAtPrice && (
                <span className="text-xl text-gray-500 line-through">
                  ${product.compareAtPrice}
                </span>
              )}
            </div>
            {product.averageRating && (
              <div className="flex items-center gap-2 mb-4">
                <span className="text-yellow-500">★</span>
                <span className="font-semibold">{product.averageRating.toFixed(1)}</span>
                <span className="text-gray-500">
                  ({product.reviewCount} reviews)
                </span>
              </div>
            )}
          </div>

          {/* Variants */}
          {product.variants.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold mb-2">Available Options:</h3>
              <div className="space-y-2">
                {product.variants.map((variant) => {
                  const isSelected = selectedVariant?.id === variant.id;
                  return (
                    <button
                      key={variant.id}
                      onClick={() => setSelectedVariant(variant)}
                      disabled={variant.stockQuantity === 0}
                      className={`w-full p-3 border-2 rounded-lg text-left transition-colors ${
                        isSelected
                          ? "border-blue-600 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      } ${
                        variant.stockQuantity === 0
                          ? "opacity-50 cursor-not-allowed"
                          : ""
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium">{variant.name}</p>
                          {variant.sku && (
                            <p className="text-sm text-gray-500">SKU: {variant.sku}</p>
                          )}
                        </div>
                        <div className="text-right">
                          {variant.price && (
                            <p className="font-semibold">${variant.price}</p>
                          )}
                          <p
                            className={`text-sm ${
                              variant.stockQuantity > 0
                                ? "text-green-600"
                                : "text-red-600"
                            }`}
                          >
                            {variant.stockQuantity > 0
                              ? `${variant.stockQuantity} in stock`
                              : "Out of stock"}
                          </p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Stock Status */}
          <div className="mb-6">
            {product.inStock ? (
              <span className="inline-block px-4 py-2 bg-green-100 text-green-800 rounded-lg">
                In Stock
              </span>
            ) : (
              <span className="inline-block px-4 py-2 bg-red-100 text-red-800 rounded-lg">
                Out of Stock
              </span>
            )}
          </div>

          {/* Description */}
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Description</h3>
            <p className="text-gray-700 whitespace-pre-line">
              {product.description || product.shortDescription}
            </p>
          </div>

          {/* Tags */}
          {product.tags.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold mb-2">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {product.tags.map((tag) => (
                  <span
                    key={tag.id}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {tag.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

