import { Router } from "express";
import * as agentController from "../controllers/agent.controller";
import { validateAgentQuery, validate } from "../middleware/validation";
import { asyncHandler } from "../middleware/errorHandler";

const router = Router();

// Query agent endpoint
router.post(
  "/query",
  validateAgentQuery(),
  validate,
  asyncHandler((req, res) => agentController.queryAgent(req, res))
);

export default router;
