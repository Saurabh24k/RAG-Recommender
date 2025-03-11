import { useState } from "react";
import { fetchRecommendations } from "../api";

export default function Recommendations() {
  const [query, setQuery] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
      if (!query.trim()) {
        console.log("⚠️ Query is empty. No API call.");
        return;
      }
      
      console.log(`🔍 Searching for: ${query}`);
      setLoading(true);
  
      try {
        const results = await fetchRecommendations(query);
        console.log("✅ API Response:", results);
      
        if (Array.isArray(results) && results.length > 0) {
          setRecommendations(results);
        } else {
          console.log("⚠️ No recommendations found.");
          setRecommendations([]); // Clear the list if no results
        }
      } catch (error) {
        console.error("❌ Error fetching recommendations:", error);
      } finally {
        setLoading(false);
      }
  };


  return (
    <div className="max-w-3xl mx-auto mt-10 p-6 bg-white shadow-lg rounded-lg">
      <h2 className="text-2xl font-bold text-center text-blue-600">Product Recommendations</h2>
      <div className="flex mt-4">
        <input
          type="text"
          className="flex-1 p-2 border rounded-l focus:outline-none"
          placeholder="Enter a product type..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-r hover:bg-blue-700"
          onClick={handleSearch}
        >
          Search
        </button>
      </div>

      {loading && <p className="mt-4 text-center">Loading...</p>}

      <ul className="mt-6 space-y-4">
        {recommendations.length === 0 && !loading && (
          <p className="text-center text-gray-500">No results found. Try a different search term.</p>
        )}
        {recommendations.map((item) => (
          <li key={item.id} className="p-4 bg-gray-100 rounded shadow">
            <h3 className="text-lg font-semibold">{item.name}</h3>
            <p className="text-sm text-gray-600">{item.description || "No description available."}</p>
            <p className="text-sm font-bold">Price: ${item.price}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
