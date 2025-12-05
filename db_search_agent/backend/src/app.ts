import express from "express";
import cors from "cors";
import env from "./config/env";
import logger from "./utils/logger";

// Import routes (will be created in next phase)
// import productRoutes from "./routes/products.routes";
// import agentRoutes from "./routes/agent.routes";

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`, {
    query: req.query,
    body: req.method !== "GET" ? req.body : undefined,
  });
  next();
});

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    environment: env.NODE_ENV,
  });
});

// Routes (commented out until routes are implemented)
// app.use("/api/products", productRoutes);
// app.use("/api/agent", agentRoutes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: "Not Found",
    message: `Route ${req.method} ${req.path} not found`,
  });
});

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error("Unhandled error", err, {
    path: req.path,
    method: req.method,
  });

  res.status(500).json({
    error: "Internal Server Error",
    message: env.NODE_ENV === "production" 
      ? "An error occurred" 
      : err.message,
  });
});

// Start server
const PORT = env.PORT;

app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`, {
    environment: env.NODE_ENV,
    port: PORT,
  });
});

export default app;

