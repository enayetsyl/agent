import { Request, Response, NextFunction } from "express";
import logger from "../utils/logger";
import env from "../config/env";

export interface AppError extends Error {
  statusCode?: number;
  isOperational?: boolean;
}

export class CustomError extends Error implements AppError {
  statusCode: number;
  isOperational: boolean;

  constructor(
    message: string,
    statusCode: number = 500,
    isOperational: boolean = true
  ) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    Error.captureStackTrace(this, this.constructor);
  }
}

export const errorHandler = (
  err: AppError | Error,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  // Log error
  logger.error("Error occurred", err, {
    path: req.path,
    method: req.method,
    statusCode: err instanceof CustomError ? err.statusCode : 500,
  });

  // Determine status code
  const statusCode = err instanceof CustomError ? err.statusCode : 500;

  // Prepare error response
  const errorResponse: any = {
    error:
      err instanceof CustomError && err.isOperational
        ? err.message
        : "Internal Server Error",
  };

  // Add error details in development mode
  if (env.NODE_ENV === "development") {
    errorResponse.message = err.message;
    if (err.stack) {
      errorResponse.stack = err.stack;
    }
  }

  // Add additional details if available
  if (err instanceof CustomError && !err.isOperational) {
    errorResponse.details = "An unexpected error occurred";
  }

  res.status(statusCode).json(errorResponse);
};

// Async handler wrapper to catch errors in async route handlers
export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};
