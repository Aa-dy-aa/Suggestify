"use client";

import React from "react";
import { BentoGrid, BentoGridItem } from "../../components/ui/bento-grid";

export default function Card({ results }) {
  console.log("Search results →", results);

  const itemsToRender =
    results && results.length > 0
      ? results.map((product, index) => ({
          title: product.title,
          description: product.explanation
            ? product.explanation
            : product.description
            ? product.description.slice(0, 120) + "..."
            : "No description available.",
          header: (
            <div className="w-full aspect-square relative rounded-xl bg-neutral-800 overflow-hidden">
              <img
                src={
                  product.imgUrl ||
                  "https://via.placeholder.com/400x400?text=No+Image"
                }
                alt={product.title}
                className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                style={{
                  background: '#222'
                }}
              />
            </div>
          ),
          icon: (
            <span className="text-white font-bold">
              {product.price ? `₹${product.price.toFixed(2)}` : "-"}
            </span>
          ),
          key: index,
        }))
      : defaultItems;

  return (
    <section className="bg-black py-10">
      <div className="max-w-5xl mx-auto px-4">
        {results && results.length > 0 && (
          <h3 className="text-white text-3xl font-bold mb-6">
            Your Searched Products ...
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
              className="bg-neutral-900 text-white border border-gray-700 hover:border-white/60 transition-all duration-200"
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
    header: (
      <div className="w-full aspect-square relative rounded-xl bg-neutral-800 overflow-hidden" />
    ),
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Digital Revolution",
    description: "Dive into the transformative power of technology.",
    header: (
      <div className="w-full aspect-square relative rounded-xl bg-neutral-800 overflow-hidden" />
    ),
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Art of Design",
    description: "Discover the beauty of thoughtful and functional design.",
    header: (
      <div className="w-full aspect-square relative rounded-xl bg-neutral-800 overflow-hidden" />
    ),
    icon: <span className="text-white font-bold">-</span>,
  },
  {
    title: "The Power of Communication",
    description:
      "Understand the impact of effective communication in our lives.",
    header: (
      <div className="w-full aspect-square relative rounded-xl bg-neutral-800 overflow-hidden" />
    ),
    icon: <span className="text-white font-bold">-</span>,
  },
];
