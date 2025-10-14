"use client";

import React, { useState, useEffect } from "react";
import { IoSearch } from "react-icons/io5";
import { BackgroundBeams } from "../../components/ui/background-beams";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const Menu = ({ setResults }) => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Fetch autocomplete suggestions
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.trim().length < 2) {
        setSuggestions([]);
        return;
      }

      try {
        const res = await fetch(`${API_BASE}/api/products/titles?limit=100`);
        if (!res.ok) throw new Error("Failed to fetch titles");
        const data = await res.json();
        const filtered = data.titles.filter((title) =>
          title.toLowerCase().includes(query.toLowerCase())
        );
        setSuggestions(filtered.slice(0, 8));
        setShowSuggestions(true);
      } catch (err) {
        console.error(err);
      }
    };

    const delay = setTimeout(fetchSuggestions, 200);
    return () => clearTimeout(delay);
  }, [query]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults([]);
    setShowSuggestions(false);

    try {
      const res = await fetch(
        `${API_BASE}/recommendations/by_title?title=${encodeURIComponent(query)}&top_n=8`
      );
      if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
      const data = await res.json();
      setResults(data.recommendations); // Update results in parent
    } catch (err) {
      setError(err.message || "Failed to fetch recommendations");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSuggestion = (title) => {
    setQuery(title);
    setShowSuggestions(false);
  };

  return (
    <div className="relative w-full h-[40rem] bg-black text-white flex items-center justify-center overflow-hidden">
      <BackgroundBeams />

      <div className="relative z-10 flex flex-col items-center justify-center px-4 w-full max-w-5xl">
        <h2 className="mb-10 sm:mb-20 text-xl sm:text-5xl text-center font-bold">
          Ask Suggestify Anything
        </h2>

        <form onSubmit={handleSubmit} className="flex flex-col w-full relative gap-2">
          <div className="relative w-full">
            <IoSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" size={20} />
            <input
              type="text"
              placeholder="Search products..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
              className="w-full px-10 py-2 rounded-md bg-transparent border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white"
            />
            {showSuggestions && suggestions.length > 0 && (
              <ul className="absolute z-20 bg-transparent backdrop-blur-md border border-white/60 rounded-md shadow-lg w-full mt-1 max-h-60 overflow-y-auto">
                {suggestions.map((title, idx) => (
                  <li
                    key={idx}
                    onMouseDown={() => handleSelectSuggestion(title)}
                    className="px-3 py-2 text-sm cursor-pointer text-white hover:bg-white/10 transition-colors duration-200"
                  >
                    {title}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </form>

        {loading && <p className="mt-4 text-gray-400">Fetching recommendations...</p>}
        {error && <p className="mt-4 text-red-500">{error}</p>}
      </div>
    </div>
  );
};

export default Menu;
