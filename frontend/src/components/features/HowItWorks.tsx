"use client";

import { FileText, Cpu, Award } from "lucide-react";

const steps = [
  {
    number: 1,
    icon: FileText,
    title: "Enter Your Usage",
    description:
      "Provide your monthly electricity usage in kWh and set your preferences for cost savings, renewable energy, and contract flexibility.",
  },
  {
    number: 2,
    icon: Cpu,
    title: "AI Analysis",
    description:
      "Our AI analyzes your usage patterns against all available energy plans in your area, considering time-of-use rates, renewable options, and contract terms.",
  },
  {
    number: 3,
    icon: Award,
    title: "Get Top 3 Picks",
    description:
      "Receive personalized recommendations with detailed explanations of why each plan matches your needs, including estimated costs and confidence scores.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="mx-auto max-w-4xl">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
          How It Works
        </h2>
        <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
          Finding the right energy plan is simple with our AI-powered recommendation engine.
        </p>

        <div className="grid gap-8 md:grid-cols-3">
          {steps.map((step) => (
            <StepCard key={step.number} {...step} />
          ))}
        </div>
      </div>
    </section>
  );
}

function StepCard({
  number,
  icon: Icon,
  title,
  description,
}: {
  number: number;
  icon: React.ElementType;
  title: string;
  description: string;
}) {
  return (
    <div className="relative flex flex-col items-center text-center p-6 rounded-xl bg-gray-50 border border-gray-100">
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 flex h-8 w-8 items-center justify-center rounded-full bg-arbor-primary text-white text-sm font-bold">
        {number}
      </div>
      <div className="mt-4 flex h-14 w-14 items-center justify-center rounded-full bg-arbor-primary/10 mb-4">
        <Icon className="h-7 w-7 text-arbor-primary" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
