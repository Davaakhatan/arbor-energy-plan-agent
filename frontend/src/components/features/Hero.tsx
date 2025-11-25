"use client";

import { Zap, TrendingDown, Leaf, Shield } from "lucide-react";

export function Hero() {
  return (
    <section className="py-16 px-4 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-4xl text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
          Find Your{" "}
          <span className="text-arbor-primary">Perfect Energy Plan</span>
        </h1>
        <p className="mt-6 text-lg text-gray-600 max-w-2xl mx-auto">
          Our AI analyzes your usage patterns and preferences to recommend the
          top 3 energy plans tailored just for you. Save money, go green, or
          find the perfect balance.
        </p>

        <div className="mt-12 grid grid-cols-2 gap-6 sm:grid-cols-4">
          <FeatureItem
            icon={TrendingDown}
            title="Save Money"
            description="Find the most cost-effective plan"
          />
          <FeatureItem
            icon={Leaf}
            title="Go Green"
            description="Choose renewable energy options"
          />
          <FeatureItem
            icon={Zap}
            title="Fast Results"
            description="Get recommendations in seconds"
          />
          <FeatureItem
            icon={Shield}
            title="Risk Aware"
            description="Understand potential trade-offs"
          />
        </div>
      </div>
    </section>
  );
}

function FeatureItem({
  icon: Icon,
  title,
  description,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col items-center text-center p-4">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-arbor-primary/10 mb-3">
        <Icon className="h-6 w-6 text-arbor-primary" />
      </div>
      <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
      <p className="text-xs text-gray-500 mt-1">{description}</p>
    </div>
  );
}
