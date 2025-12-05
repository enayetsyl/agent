import { Router } from "express";
import * as productController from "../controllers/products.controller";
import {
  validateProductSearch,
  validateProductId,
  validateProductSlug,
  validateAvailabilityCheck,
  validate,
} from "../middleware/validation";
import { asyncHandler } from "../middleware/errorHandler";

const router = Router();

// Search products
router.get(
  "/search",
  validateProductSearch(),
  validate,
  asyncHandler((req, res) => productController.searchProducts(req, res))
);

// Get all categories
router.get(
  "/categories",
  asyncHandler((req, res) => productController.getCategories(req, res))
);

// Check product availability
router.get(
  "/:id/availability",
  validateAvailabilityCheck(),
  validate,
  asyncHandler((req, res) => productController.checkAvailability(req, res))
);

// Get product by slug
router.get(
  "/slug/:slug",
  validateProductSlug(),
  validate,
  asyncHandler((req, res) => productController.getProductBySlug(req, res))
);

// Get product by ID (must be last to avoid matching other routes)
router.get(
  "/:id",
  validateProductId(),
  validate,
  asyncHandler((req, res) => productController.getProduct(req, res))
);

export default router;
