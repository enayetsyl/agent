import { Request, Response, NextFunction } from "express";
import {
  validationResult,
  ValidationChain,
  query,
  param,
  body,
} from "express-validator";
import { CustomError } from "./errorHandler";

// Middleware to check validation results
export const validate = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    const errorMessages = errors.array().map((err) => ({
      field: err.type === "field" ? err.path : undefined,
      message: err.msg,
    }));

    throw new CustomError("Validation failed", 400);
  }

  next();
};

// Validation rules for product search
export const validateProductSearch = (): ValidationChain[] => {
  return [
    query("q")
      .optional()
      .isString()
      .trim()
      .notEmpty()
      .withMessage("Query must be a non-empty string"),
    query("category")
      .optional()
      .isString()
      .trim()
      .withMessage("Category must be a string"),
    query("minPrice")
      .optional()
      .isFloat({ min: 0 })
      .withMessage("Min price must be a positive number"),
    query("maxPrice")
      .optional()
      .isFloat({ min: 0 })
      .withMessage("Max price must be a positive number"),
    query("brand")
      .optional()
      .isString()
      .trim()
      .withMessage("Brand must be a string"),
    query("inStock")
      .optional()
      .isBoolean()
      .withMessage("In stock must be a boolean"),
    query("featured")
      .optional()
      .isBoolean()
      .withMessage("Featured must be a boolean"),
    query("tags")
      .optional()
      .isString()
      .withMessage("Tags must be a comma-separated string"),
    query("limit")
      .optional()
      .isInt({ min: 1, max: 100 })
      .withMessage("Limit must be between 1 and 100"),
    query("offset")
      .optional()
      .isInt({ min: 0 })
      .withMessage("Offset must be a non-negative integer"),
  ];
};

// Validation rules for product ID
export const validateProductId = (): ValidationChain[] => {
  return [
    param("id")
      .isInt({ min: 1 })
      .withMessage("Product ID must be a positive integer"),
  ];
};

// Validation rules for product slug
export const validateProductSlug = (): ValidationChain[] => {
  return [
    param("slug")
      .isString()
      .trim()
      .notEmpty()
      .withMessage("Slug must be a non-empty string"),
  ];
};

// Validation rules for availability check
export const validateAvailabilityCheck = (): ValidationChain[] => {
  return [
    param("id")
      .isInt({ min: 1 })
      .withMessage("Product ID must be a positive integer"),
    query("size")
      .optional()
      .isString()
      .trim()
      .withMessage("Size must be a string"),
    query("color")
      .optional()
      .isString()
      .trim()
      .withMessage("Color must be a string"),
  ];
};

// Validation rules for agent query
export const validateAgentQuery = (): ValidationChain[] => {
  return [
    body("message")
      .isString()
      .trim()
      .notEmpty()
      .withMessage("Message is required and must be a non-empty string")
      .isLength({ min: 1, max: 1000 })
      .withMessage("Message must be between 1 and 1000 characters"),
    body("sessionId")
      .optional()
      .isString()
      .trim()
      .withMessage("Session ID must be a string"),
  ];
};
