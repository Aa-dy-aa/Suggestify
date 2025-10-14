"use client";

import React, { useState } from "react";
import { IoSearch } from "react-icons/io5";
import { HoverBorderGradient } from "../../components/ui/hover-border-gradient"

const Navbar = () => {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    console.log("Searching for:", searchQuery);
  };

  return (
    <nav className="bg-black text-white px-6 py-4 flex justify-between items-center">
      {/* Left: Logo + Website Name */}
      <div className="flex items-center gap-2">
        <svg
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M12 2L15 8H9L12 2Z" fill="#7600FF" />
          <circle cx="12" cy="16" r="6" fill="#FFA0A0" />
        </svg>
        <div className="text-xl font-bold">Suggestify</div>
      </div>

      {/* Right: Compact, rounded search form with Aceternity effect */}
      <form onSubmit={handleSearchSubmit}>
        <HoverBorderGradient
          containerClassName="rounded-full"
          as="div"
          className="flex items-center h-9 bg-transparent text-white px-2"
        >
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-full w-32 bg-transparent text-white placeholder-gray-400 focus:outline-none px-2"
          />
          <button
            type="submit"
            className="h-full px-2 text-white hover:bg-gray-800 rounded-full flex items-center justify-center transition"
          >
            <IoSearch size={16} />
          </button>
        </HoverBorderGradient>
      </form>
    </nav>
  );
};

export default Navbar;
