import logger from "../utils/logger";
import { CustomError } from "../middleware/errorHandler";
import env from "../config/env";

const AGENT_SERVER_URL = env.AGENT_SERVER_URL || "http://localhost:8000";

export async function queryAgent(
  userMessage: string,
  sessionId: string
): Promise<string> {
  try {
    logger.info("Agent query received", {
      message: userMessage,
      sessionId,
    });

    // Call Python agent HTTP server
    const response = await fetch(`${AGENT_SERVER_URL}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userMessage,
        sessionId: sessionId || undefined,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      logger.error("Agent server error", {
        status: response.status,
        statusText: response.statusText,
        error: errorText,
      });
      throw new CustomError(
        `Agent server error: ${response.statusText}`,
        response.status
      );
    }

    const data = await response.json();

    if (data.status === "error") {
      logger.error("Agent returned error", { error: data.error });
      throw new CustomError(
        data.error || "Agent returned an error",
        500
      );
    }

    logger.info("Agent query successful", {
      sessionId,
      responseLength: data.response?.length || 0,
    });

    return data.response || "No response from agent";
  } catch (error) {
    if (error instanceof CustomError) {
      throw error;
    }
    logger.error("Error querying agent", error);
    throw new CustomError("Failed to query agent", 500);
  }
}
