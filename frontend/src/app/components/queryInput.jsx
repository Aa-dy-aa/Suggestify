"use client";

import React, { FormEvent, useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SearchForm = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
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

    const delay = setTimeout(fetchSuggestions, 200); // debounce
    return () => clearTimeout(delay);
  }, [query]);

  // Handle search submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults([]);
    setShowSuggestions(false);

    try {
      const res = await fetch(
        `${API_BASE}/recommendations/by_title?title=${encodeURIComponent(
          query
        )}&top_n=5`
      );

      if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);

      const data = await res.json();
      setResults(data.recommendations);
    } catch (err) {
      setError(err.message || "Failed to fetch recommendations");
    } finally {
      setLoading(false);
    }
  };

  // Handle click on suggestion
  const handleSelectSuggestion = (title) => {
    setQuery(title);
    setShowSuggestions(false);
  };

  return (
    <div className="flex flex-col items-center gap-6 p-6 relative">
      {/* Search Form */}
      <form
        onSubmit={handleSubmit}
        className="flex items-center max-w-sm w-full mx-auto relative"
      >
        <label htmlFor="simple-search" className="sr-only">
          Search
        </label>
        <div className="relative w-full">
          <div className="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
            <svg
              className="w-4 h-4 text-gray-500 dark:text-gray-400"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 18 20"
            >
              <path
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M3 5v10M3 5a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm0 10a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm12 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm0 0V6a3 3 0 0 0-3-3H9m1.5-2-2 2 2 2"
              />
            </svg>
          </div>
          <input
            type="text"
            id="simple-search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg 
                       focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5  
                       dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 
                       dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            placeholder="Search Products"
            required
          />
          {/* Autocomplete Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <ul className="absolute z-10 bg-white border border-gray-300 rounded-md shadow-md w-full mt-1 max-h-60 overflow-y-auto dark:bg-gray-800 dark:border-gray-600">
              {suggestions.map((title, idx) => (
                <li
                  key={idx}
                  onMouseDown={() => handleSelectSuggestion(title)}
                  className="px-3 py-2 text-sm cursor-pointer hover:bg-blue-100 dark:hover:bg-gray-700"
                >
                  {title}
                </li>
              ))}
            </ul>
          )}
        </div>
        <button
          type="submit"
          className="p-2.5 ms-2 text-sm font-medium text-white bg-blue-700 rounded-lg 
                     border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none 
                     focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
        >
          <svg
            className="w-4 h-4"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 20 20"
          >
            <path
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
            />
          </svg>
          <span className="sr-only">Search</span>
        </button>
      </form>

      {/* Loading / Error / Results */}
      {loading && <p className="text-gray-500 mt-2">Fetching recommendations...</p>}
      {error && <p className="text-red-500 mt-2">{error}</p>}

      <div className="w-full max-w-md space-y-4 mt-4">
        {results.map((product, index) => (
          <div
            key={index}
            className="p-4 border rounded-lg shadow-md bg-white dark:bg-gray-800"
          >
            <h3 className="font-semibold text-lg text-blue-700 dark:text-blue-400">
              {product.title}
            </h3>
            {product.description && (
              <p className="text-gray-700 dark:text-gray-300 text-sm mt-1">
                {product.description.slice(0, 100)}...
              </p>
            )}
            <p className="text-sm text-gray-500 mt-1">
              <span className="font-medium">Category:</span>{" "}
              {product.category_name || "Unknown"}
            </p>
            {product.price && (
              <p className="text-sm text-green-600 mt-1">
                ₹{product.price.toFixed(2)}
              </p>
            )}
            {product.similarity_score && (
              <p className="text-sm text-gray-400">
                Similarity: {(product.similarity_score * 100).toFixed(1)}%
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchForm;
