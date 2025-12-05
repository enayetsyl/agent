import { Request, Response } from "express";
import * as agentService from "../services/agent.service";
import { CustomError } from "../middleware/errorHandler";
import logger from "../utils/logger";

export async function queryAgent(req: Request, res: Response): Promise<void> {
  try {
    const { message, sessionId } = req.body;

    if (!message || typeof message !== "string" || message.trim().length === 0) {
      throw new CustomError("Message is required and must be a non-empty string", 400);
    }

    const response = await agentService.queryAgent(
      message.trim(),
      sessionId || ""
    );

    res.json({ response });
  } catch (error) {
    logger.error("Error in queryAgent controller", error);
    throw error; // Let errorHandler middleware handle it
  }
}

