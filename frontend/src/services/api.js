import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

/**
 * POST /api/risk — Full risk assessment for a city.
 * Maps to pseudocode MAIN flow: Steps 1–9.
 */
export async function getRiskReport(cityName) {
  const response = await api.post("/risk", { city_name: cityName });
  return response.data;
}

/**
 * GET /api/history — Recent search history.
 */
export async function getHistory() {
  const response = await api.get("/history");
  return response.data;
}

/**
 * GET /api/health — Health check.
 */
export async function checkHealth() {
  const response = await api.get("/health");
  return response.data;
}

export default api;
