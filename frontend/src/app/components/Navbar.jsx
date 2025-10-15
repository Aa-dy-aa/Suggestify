"use client";

import React, { useState } from "react";
import { IoSearch } from "react-icons/io5";
import { HoverBorderGradient } from "../../components/ui/hover-border-gradient";

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
        {/* ✅ SVG without XML declaration */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 512 512"
          className="w-8 h-8"
        >
          <path
            fill="#458FDE"
            d="M504.026,192.375C475.738,81.771,375.42,0,256,0C114.616,0,0,114.616,0,256
            c0,119.42,81.771,219.738,192.375,248.026L504.026,192.375z"
          />
          <path
            fill="#4D68B5"
            d="M512,256c0-21.965-2.77-43.282-7.974-63.625l-75.504-75.506L83.478,395.13l108.896,108.896
            C212.718,509.23,234.035,512,256,512C397.385,512,512,397.385,512,256z"
          />
          <polygon fill="#CCCCCC" points="428.522,161.391 233.739,139.13 256,395.13 428.522,395.13" />
          <polygon fill="#E5E5E5" points="83.478,161.391 83.478,395.13 256,395.13 256,139.13" />
          <polygon fill="#F2F2F2" points="256,183.652 211.478,278.261 256,372.87 406.261,372.87 406.261,183.652" />
          <rect x="105.739" y="183.652" fill="#FFFFFF" width="150.261" height="189.217" />
        </svg>

        <div className="text-xl font-bold">Suggestify</div>
      </div>

      {/* Right: Search box */}
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
