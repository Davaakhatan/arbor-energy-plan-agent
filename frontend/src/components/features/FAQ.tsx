"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

const faqs = [
  {
    question: "How does the AI recommendation work?",
    answer:
      "Our AI analyzes your monthly electricity usage, time-of-use patterns, and preferences to match you with the best available plans. It considers factors like base rates, time-of-use pricing, renewable energy percentages, contract terms, and early termination fees to find plans that align with your priorities.",
  },
  {
    question: "What information do I need to provide?",
    answer:
      "You'll need your average monthly electricity usage in kWh (found on your electricity bill) and your preferences for cost savings, renewable energy, and contract flexibility. The more accurate your usage data, the better our recommendations will be.",
  },
  {
    question: "Is my data secure?",
    answer:
      "Yes, we take data security seriously. Your usage information is only used to generate recommendations and is not shared with third parties. We use industry-standard encryption to protect your data.",
  },
  {
    question: "How accurate are the cost estimates?",
    answer:
      "Our cost estimates are based on the plan rates and your provided usage. Actual costs may vary based on seasonal usage changes, time-of-use patterns, and any promotional rates that may expire. We recommend reviewing the full plan details before switching.",
  },
  {
    question: "Can I switch plans easily?",
    answer:
      "Yes! Once you've found a plan you like, you can typically switch by contacting the energy provider directly. Be sure to check your current contract for any early termination fees before switching.",
  },
  {
    question: "What areas do you cover?",
    answer:
      "We currently cover deregulated energy markets in the United States, including Texas, Pennsylvania, Ohio, and other states with competitive electricity markets. Enter your ZIP code to see available plans in your area.",
  },
];

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section id="faq" className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="mx-auto max-w-3xl">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
          Frequently Asked Questions
        </h2>
        <p className="text-center text-gray-600 mb-12">
          Have questions? We&apos;ve got answers.
        </p>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <FAQItem
              key={index}
              question={faq.question}
              answer={faq.answer}
              isOpen={openIndex === index}
              onClick={() => setOpenIndex(openIndex === index ? null : index)}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

function FAQItem({
  question,
  answer,
  isOpen,
  onClick,
}: {
  question: string;
  answer: string;
  isOpen: boolean;
  onClick: () => void;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <button
        type="button"
        className="w-full flex items-center justify-between px-6 py-4 text-left focus:outline-none focus:ring-2 focus:ring-arbor-primary focus:ring-inset"
        onClick={onClick}
        aria-expanded={isOpen}
      >
        <span className="font-medium text-gray-900">{question}</span>
        <ChevronDown
          className={`h-5 w-5 text-gray-500 transition-transform duration-200 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>
      {isOpen && (
        <div className="px-6 pb-4">
          <p className="text-gray-600">{answer}</p>
        </div>
      )}
    </div>
  );
}
