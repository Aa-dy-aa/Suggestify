"use client";

import React from "react";
import { BentoGrid, BentoGridItem } from "../../components/ui/bento-grid";

export default function Card({ results }) {
  // Use default items if no results are provided
  const itemsToRender =
    results && results.length > 0
      ? results.map((product, index) => ({
          title: product.title,
          description: product.description
            ? product.description.slice(0, 100) + "..."
            : "",
          header: <div className="flex flex-1 w-full h-24 rounded-xl bg-neutral-800" />,
          icon: (
            <span className="text-white font-bold">
              {product.price ? `₹${product.price.toFixed(2)}` : "-"}
            </span>
          ),
          key: index,
        }))
      : defaultItems;

  return (
    <section className="bg-black py-10"> {/* Entire section background black */}
      <div className="max-w-5xl mx-auto px-4">
        {results && results.length > 0 && (
          <h3 className="text-white text-3xl font-bold mb-6">
            Your search results...
          </h3>
        )}

        <BentoGrid className="gap-4 grid-cols-1 md:grid-cols-4">
          {itemsToRender.map((item, i) => (
            <BentoGridItem
              key={i}
              title={item.title}
              description={item.description}
              header={item.header}
              icon={item.icon}
              className="bg-neutral-900 text-white"
            />
          ))}
        </BentoGrid>
      </div>
    </section>
  );
}

// Default static items
const defaultItems = [
  {
    title: "The Dawn of Innovation",
    description: "Explore the birth of groundbreaking ideas and inventions.",
    header: <div className="flex flex-1 w-full h-24 rounded-xl bg-neutral-800" />,
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Digital Revolution",
    description: "Dive into the transformative power of technology.",
    header: <div className="flex flex-1 w-full h-24 rounded-xl bg-neutral-800" />,
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Art of Design",
    description: "Discover the beauty of thoughtful and functional design.",
    header: <div className="flex flex-1 w-full h-24 rounded-xl bg-neutral-800" />,
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Power of Communication",
    description: "Understand the impact of effective communication in our lives.",
    header: <div className="flex flex-1 w-full h-24 rounded-xl bg-neutral-800" />,
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Pursuit of Knowledge",
    description: "Join the quest for understanding and enlightenment.",
    header: <div className="flex flex-1 w-full h-24 rounded-xl bg-neutral-800" />,
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Joy of Creation",
    description: "Experience the thrill of bringing ideas to life.",
    header: <div className="flex flex-1 w-full h-24 rounded-xl bg-neutral-800" />,
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Spirit of Adventure",
    description: "Embark on exciting journeys and thrilling discoveries.",
    header: <div className="flex flex-1 w-full h-24 rounded-xl bg-neutral-800" />,
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Path of Discovery",
    description: "Unlock new insights and expand your horizons.",
    header: <div className="flex flex-1 w-full h-24 rounded-xl bg-neutral-800" />,
    icon: <span className="text-white font-bold">-</span>,
  },
];
