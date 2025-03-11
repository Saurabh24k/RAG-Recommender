import axios from "axios";

const API_BASE_URL = "http://localhost:8000"; // Make sure this matches your backend

export const fetchRecommendations = async (query) => {
  try {
    console.log(`🌍 Sending request to: ${API_BASE_URL}/recommendations?query=${query}`);
    
    const response = await axios.get(`${API_BASE_URL}/recommendations`, {
      params: { query },
    });

    console.log("📩 Raw API Response:", response);

    return response.data; // Ensure the API is returning an array
  } catch (error) {
    console.error("❌ API Error:", error.response ? error.response.data : error.message);
    return [];
  }
};
