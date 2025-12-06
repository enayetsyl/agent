"use client";

interface PriceFilterProps {
  minPrice?: number;
  maxPrice?: number;
  onMinPriceChange: (price: number | undefined) => void;
  onMaxPriceChange: (price: number | undefined) => void;
}

export default function PriceFilter({
  minPrice,
  maxPrice,
  onMinPriceChange,
  onMaxPriceChange,
}: PriceFilterProps) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Price Range
      </label>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <input
            type="number"
            placeholder="Min"
            value={minPrice || ""}
            onChange={(e) =>
              onMinPriceChange(
                e.target.value ? parseFloat(e.target.value) : undefined
              )
            }
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            min="0"
            step="0.01"
          />
        </div>
        <div>
          <input
            type="number"
            placeholder="Max"
            value={maxPrice || ""}
            onChange={(e) =>
              onMaxPriceChange(
                e.target.value ? parseFloat(e.target.value) : undefined
              )
            }
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            min="0"
            step="0.01"
          />
        </div>
      </div>
    </div>
  );
}

