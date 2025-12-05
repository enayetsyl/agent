import { Request, Response } from "express";
import * as productService from "../services/product.service";
import { ProductSearchFilters } from "../types";
import { CustomError } from "../middleware/errorHandler";
import logger from "../utils/logger";

export async function searchProducts(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const filters: ProductSearchFilters = {
      query: req.query.q as string | undefined,
      category: req.query.category as string | undefined,
      minPrice: req.query.minPrice ? Number(req.query.minPrice) : undefined,
      maxPrice: req.query.maxPrice ? Number(req.query.maxPrice) : undefined,
      brand: req.query.brand as string | undefined,
      inStock: req.query.inStock === "true" ? true : undefined,
      featured: req.query.featured === "true" ? true : undefined,
      tags: req.query.tags
        ? (req.query.tags as string).split(",").map((t) => t.trim())
        : undefined,
      limit: req.query.limit ? Number(req.query.limit) : undefined,
      offset: req.query.offset ? Number(req.query.offset) : undefined,
    };

    const result = await productService.searchProducts(filters);
    res.json(result);
  } catch (error) {
    logger.error("Error in searchProducts controller", error);
    throw error; // Let errorHandler middleware handle it
  }
}

export async function getProduct(req: Request, res: Response): Promise<void> {
  try {
    const { id } = req.params;
    const productId = Number(id);

    if (isNaN(productId)) {
      throw new CustomError("Invalid product ID", 400);
    }

    const product = await productService.getProductById(productId);

    if (!product) {
      throw new CustomError("Product not found", 404);
    }

    res.json(product);
  } catch (error) {
    logger.error("Error in getProduct controller", error);
    throw error; // Let errorHandler middleware handle it
  }
}

export async function getProductBySlug(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const { slug } = req.params;

    if (!slug) {
      throw new CustomError("Slug is required", 400);
    }

    const product = await productService.getProductBySlug(slug);

    if (!product) {
      throw new CustomError("Product not found", 404);
    }

    res.json(product);
  } catch (error) {
    logger.error("Error in getProductBySlug controller", error);
    throw error; // Let errorHandler middleware handle it
  }
}

export async function checkAvailability(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const { id } = req.params;
    const { size, color } = req.query;
    const productId = Number(id);

    if (isNaN(productId)) {
      throw new CustomError("Invalid product ID", 400);
    }

    const availability = await productService.checkAvailability(
      productId,
      size as string | undefined,
      color as string | undefined
    );

    res.json(availability);
  } catch (error) {
    logger.error("Error in checkAvailability controller", error);
    throw error; // Let errorHandler middleware handle it
  }
}

export async function getCategories(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const categories = await productService.getCategories();
    res.json(categories);
  } catch (error) {
    logger.error("Error in getCategories controller", error);
    throw error; // Let errorHandler middleware handle it
  }
}
