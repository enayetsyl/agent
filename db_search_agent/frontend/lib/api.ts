import axios from "axios";

// Backend API URL (for product endpoints)
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001/api";

// Agent Server URL (direct connection, bypasses Express)
const AGENT_SERVER_URL =
  process.env.NEXT_PUBLIC_AGENT_SERVER_URL || "http://localhost:8000";

export const api = {
  products: {
    search: async (filters: {
      q?: string;
      category?: string;
      minPrice?: number;
      maxPrice?: number;
      brand?: string;
      inStock?: boolean;
      featured?: boolean;
      limit?: number;
      offset?: number;
    }) => {
      const response = await axios.get(`${API_BASE_URL}/products/search`, {
        params: filters,
      });
      return response.data;
    },
    getById: async (id: number) => {
      const response = await axios.get(`${API_BASE_URL}/products/${id}`);
      return response.data;
    },
    getBySlug: async (slug: string) => {
      const response = await axios.get(`${API_BASE_URL}/products/slug/${slug}`);
      return response.data;
    },
    checkAvailability: async (id: number, size?: string, color?: string) => {
      const response = await axios.get(
        `${API_BASE_URL}/products/${id}/availability`,
        {
          params: { size, color },
        }
      );
      return response.data;
    },
    getCategories: async () => {
      const response = await axios.get(`${API_BASE_URL}/products/categories`);
      return response.data;
    },
  },
  agent: {
    // Direct connection to agent server (bypasses Express backend)
    query: async (message: string, sessionId: string) => {
      const response = await axios.post(`${AGENT_SERVER_URL}/query`, {
        message,
        sessionId,
      });
      return response.data;
    },
  },
};

