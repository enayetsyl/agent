import prisma from "../config/database";
import { Prisma } from "@prisma/client";
import { ProductSearchFilters, Product, ProductAvailability } from "../types";
import logger from "../utils/logger";
import { CustomError } from "../middleware/errorHandler";

// Private helper function to format product data
function formatProduct(product: any): Product {
  const reviews = product.reviews || [];
  const avgRating =
    reviews.length > 0 && reviews.some((r: any) => r.rating !== null)
      ? reviews.reduce((sum: number, r: any) => sum + (r.rating || 0), 0) /
        reviews.filter((r: any) => r.rating !== null).length
      : null;

  const variants = product.variants || [];
  const images = product.images || [];
  const tags = product.tags || [];

  return {
    id: product.id,
    name: product.name,
    slug: product.slug,
    description: product.description,
    shortDescription: product.shortDescription,
    price: Number(product.price),
    compareAtPrice: product.compareAtPrice
      ? Number(product.compareAtPrice)
      : null,
    category: product.category,
    brand: product.brand,
    image: images[0]?.url || null,
    images: images.map((img: any) => ({
      url: img.url,
      altText: img.altText,
      isPrimary: img.isPrimary || false,
    })),
    variants: variants.map((v: any) => ({
      id: v.id,
      name: v.name,
      sku: v.sku,
      price: v.price ? Number(v.price) : null,
      stockQuantity: v.stockQuantity ?? 0,
      attributes: v.attributes.reduce((acc: any, attr: any) => {
        acc[attr.attributeName] = attr.attributeValue;
        return acc;
      }, {}),
    })),
    tags: tags.map((t: any) => t.tag),
    averageRating: avgRating,
    reviewCount: reviews.length,
    inStock: variants.some((v: any) => (v.stockQuantity ?? 0) > 0),
  };
}

export async function searchProducts(filters: ProductSearchFilters) {
  const {
    query,
    category,
    minPrice,
    maxPrice,
    brand,
    inStock,
    featured,
    tags,
    limit = 20,
    offset = 0,
  } = filters;

  const where: Prisma.ProductWhereInput = {
    status: "active",
  };

  // Text search
  if (query) {
    where.OR = [
      { name: { contains: query, mode: "insensitive" } },
      { description: { contains: query, mode: "insensitive" } },
      { shortDescription: { contains: query, mode: "insensitive" } },
      { brand: { contains: query, mode: "insensitive" } },
    ];
  }

  // Category filter
  if (category) {
    where.category = {
      OR: [
        { slug: category },
        { name: { contains: category, mode: "insensitive" } },
      ],
    };
  }

  // Price filters
  if (minPrice !== undefined || maxPrice !== undefined) {
    where.price = {};
    if (minPrice !== undefined) {
      where.price.gte = minPrice;
    }
    if (maxPrice !== undefined) {
      where.price.lte = maxPrice;
    }
  }

  // Brand filter
  if (brand) {
    where.brand = { contains: brand, mode: "insensitive" };
  }

  // Featured filter
  if (featured !== undefined) {
    where.featured = featured;
  }

  // Tags filter
  if (tags && tags.length > 0) {
    where.tags = {
      some: {
        tag: {
          slug: { in: tags },
        },
      },
    };
  }

  // Stock filter
  if (inStock) {
    where.variants = {
      some: {
        stockQuantity: { gt: 0 },
      },
    };
  }

  try {
    const [products, total] = await Promise.all([
      prisma.product.findMany({
        where,
        include: {
          category: true,
          images: {
            where: { isPrimary: true },
            take: 1,
          },
          variants: {
            include: {
              attributes: true,
            },
          },
          tags: {
            include: {
              tag: true,
            },
          },
          reviews: {
            select: {
              rating: true,
            },
          },
        },
        orderBy: featured
          ? [{ featured: "desc" }, { createdAt: "desc" }]
          : { createdAt: "desc" },
        take: limit,
        skip: offset,
      }),
      prisma.product.count({ where }),
    ]);

    return {
      products: products.map((p) => formatProduct(p)),
      total,
      limit,
      offset,
    };
  } catch (error) {
    logger.error("Error searching products", error);
    throw new CustomError("Failed to search products", 500);
  }
}

export async function getProductById(id: number): Promise<Product | null> {
  try {
    const product = await prisma.product.findUnique({
      where: { id },
      include: {
        category: true,
        images: {
          orderBy: [{ sortOrder: "asc" }, { isPrimary: "desc" }],
        },
        variants: {
          include: {
            attributes: true,
            images: true,
          },
        },
        tags: {
          include: {
            tag: true,
          },
        },
        reviews: {
          select: {
            rating: true,
          },
          orderBy: { createdAt: "desc" },
          take: 10,
          skip: 0,
        },
      },
    });

    if (!product) {
      return null;
    }

    return formatProduct(product);
  } catch (error) {
    logger.error("Error getting product by ID", error);
    throw new CustomError("Failed to get product", 500);
  }
}

export async function getProductBySlug(slug: string): Promise<Product | null> {
  try {
    const product = await prisma.product.findUnique({
      where: { slug },
      include: {
        category: true,
        images: {
          orderBy: [{ sortOrder: "asc" }, { isPrimary: "desc" }],
        },
        variants: {
          include: {
            attributes: true,
            images: true,
          },
        },
        tags: {
          include: {
            tag: true,
          },
        },
        reviews: {
          select: {
            rating: true,
          },
          orderBy: { createdAt: "desc" },
          take: 10,
          skip: 0,
        },
      },
    });

    if (!product) {
      return null;
    }

    return formatProduct(product);
  } catch (error) {
    logger.error("Error getting product by slug", error);
    throw new CustomError("Failed to get product", 500);
  }
}

export async function checkAvailability(
  productId: number,
  size?: string,
  color?: string
): Promise<ProductAvailability> {
  try {
    const product = await prisma.product.findUnique({
      where: { id: productId },
      include: {
        variants: {
          include: {
            attributes: true,
          },
        },
      },
    });

    if (!product) {
      return { available: false, message: "Product not found" };
    }

    let matchingVariants = product.variants;

    if (size) {
      matchingVariants = matchingVariants.filter((v) =>
        v.attributes.some(
          (a) =>
            a.attributeName === "size" &&
            a.attributeValue.toLowerCase() === size.toLowerCase()
        )
      );
    }

    if (color) {
      matchingVariants = matchingVariants.filter((v) =>
        v.attributes.some(
          (a) =>
            a.attributeName === "color" &&
            a.attributeValue.toLowerCase() === color.toLowerCase()
        )
      );
    }

    const availableVariants = matchingVariants.filter(
      (v) => (v.stockQuantity ?? 0) > 0
    );

    return {
      available: availableVariants.length > 0,
      variants: availableVariants.map((v) => ({
        id: v.id,
        name: v.name,
        stockQuantity: v.stockQuantity ?? 0,
        price: v.price ? Number(v.price) : Number(product.price),
        attributes: v.attributes.reduce((acc, attr) => {
          acc[attr.attributeName] = attr.attributeValue;
          return acc;
        }, {} as Record<string, string>),
      })),
      totalStock: availableVariants.reduce(
        (sum, v) => sum + (v.stockQuantity ?? 0),
        0
      ),
    };
  } catch (error) {
    logger.error("Error checking availability", error);
    throw new CustomError("Failed to check availability", 500);
  }
}

export async function getCategories() {
  try {
    return prisma.category.findMany({
      where: { parentId: null },
      include: {
        children: true,
      },
      orderBy: { name: "asc" },
    });
  } catch (error) {
    logger.error("Error getting categories", error);
    throw new CustomError("Failed to get categories", 500);
  }
}
