"use client";
import Navbar from "./components/Navbar";
import Menu from "./components/Menu";
import Card from "./components/Card";
import { useState } from "react";

export default function Home() {
  const [results, setResults] = useState([]);

  return (
    <div>
      <Navbar />
      <Menu setResults={setResults} /> {/* Pass setter to Menu */}
      <Card results={results} /> {/* Pass results to Card */}
    </div>
  );
}
