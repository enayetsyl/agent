import ProductSearch from "@/components/ProductSearch";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">Product Catalog</h1>
          <p className="text-gray-600 text-lg mb-6">
            Search and discover products in our catalog
          </p>
          <Link
            href="/products"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Browse All Products
          </Link>
        </div>
        <ProductSearch />
      </div>
    </main>
  );
}
