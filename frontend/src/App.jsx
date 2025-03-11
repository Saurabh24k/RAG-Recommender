import { useState, useEffect } from "react";
import axios from "axios";

const ProductCard = ({ product }) => {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="bg-white shadow-lg p-6 rounded-lg border border-gray-200 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
      <h2 className="text-xl font-semibold text-gray-900 mb-2">{product.name}</h2>
      <p className="text-gray-700 transition-all duration-300">
        {expanded ? product.description : `${product.description.substring(0, 200)}...`}
      </p>
      {product.description.length > 200 && (
        <button
          className="text-blue-500 mt-2 hover:underline focus:outline-none transition-colors duration-200"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Read Less" : "Read More"}
        </button>
      )}
      <p className="text-lg font-bold mt-4 text-gray-900">Price: ${product.price.toFixed(2)}</p>
    </div>
  );
};

export default function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    if (searchQuery.length > 1 && showSuggestions) {
      axios
        .get(`http://localhost:8000/suggestions?query=${searchQuery}`)
        .then((res) => {
          setSuggestions(res.data);
        })
        .catch((err) => console.error("Error fetching suggestions:", err));
    } else {
      setSuggestions([]);
    }
  }, [searchQuery, showSuggestions]);

  const fetchRecommendations = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setShowSuggestions(false);
    try {
      const response = await axios.get(`http://localhost:8000/recommendations?query=${searchQuery}`);
      setRecommendations(response.data);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    }
    setLoading(false);
  };

  const handleSuggestionClick = (keyword) => {
    setSearchQuery(keyword);
    setShowSuggestions(false);
    fetchRecommendations();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Hero Section */}
      <div className="text-center py-20 bg-gradient-to-r from-blue-600 to-purple-600 animate-fade-in">
        <h1 className="text-5xl font-bold text-white mb-4 animate-slide-in-top">
          Discover Your Perfect Product
        </h1>
        <p className="text-xl text-blue-100 mb-8 animate-slide-in-bottom">
          Powered by AI-driven recommendations. Start searching below!
        </p>

        {/* Search Bar */}
        <div className="relative max-w-2xl mx-auto px-4 animate-fade-in">
          <div className="flex items-center bg-white rounded-lg shadow-lg overflow-hidden">
            <input
              type="text"
              placeholder="Search for a product..."
              className="w-full p-4 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowSuggestions(true);
              }}
              onKeyDown={(e) => e.key === "Enter" && fetchRecommendations()}
              onFocus={() => setShowSuggestions(true)}
            />
            <button
              className="px-8 py-4 bg-blue-600 text-white hover:bg-blue-700 transition-all duration-200 focus:outline-none transform hover:scale-105"
              onClick={fetchRecommendations}
            >
              Search
            </button>
          </div>

          {/* Suggestions Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <ul className="absolute w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-2 z-10 max-h-60 overflow-y-auto animate-fade-in">
              {suggestions.map((keyword, index) => (
                <li
                  key={index}
                  className="p-3 cursor-pointer hover:bg-blue-50 transition-all duration-200 transform hover:translate-x-2"
                  onClick={() => handleSuggestionClick(keyword)}
                >
                  {keyword}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Results Section */}
      <div className="container mx-auto p-8">
        {/* Loading Indicator */}
        {loading && (
          <div className="flex justify-center mt-8 animate-fade-in">
            <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        )}

        {/* Results Grid */}
        {recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-8 animate-fade-in">
            {recommendations.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          !loading && (
            <div className="text-center mt-12 animate-fade-in">
              <p className="text-2xl text-gray-700">No results found.</p>
              <p className="text-gray-500 mt-2">Try searching for something else!</p>
            </div>
          )
        )}
      </div>
    </div>
  );
}