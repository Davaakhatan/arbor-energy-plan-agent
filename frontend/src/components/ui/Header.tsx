"use client";

import { useState } from "react";
import { Leaf, Menu, X } from "lucide-react";
import Link from "next/link";

export function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="border-b bg-white" role="banner">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="flex items-center gap-2"
          aria-label="Arbor Energy - Home"
        >
          <Leaf className="h-8 w-8 text-arbor-primary" aria-hidden="true" />
          <span className="text-xl font-bold text-gray-900">Arbor Energy</span>
        </Link>

        {/* Desktop navigation */}
        <nav
          className="hidden md:flex items-center gap-6"
          role="navigation"
          aria-label="Main navigation"
        >
          <Link
            href="#how-it-works"
            className="text-sm font-medium text-gray-600 hover:text-arbor-primary transition-colors focus:outline-none focus:ring-2 focus:ring-arbor-primary focus:ring-offset-2 rounded"
          >
            How It Works
          </Link>
          <Link
            href="#faq"
            className="text-sm font-medium text-gray-600 hover:text-arbor-primary transition-colors focus:outline-none focus:ring-2 focus:ring-arbor-primary focus:ring-offset-2 rounded"
          >
            FAQ
          </Link>
        </nav>

        {/* Mobile menu button */}
        <button
          type="button"
          className="md:hidden p-2 rounded-md text-gray-600 hover:text-arbor-primary hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-arbor-primary"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-expanded={isMobileMenuOpen}
          aria-controls="mobile-menu"
          aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
        >
          {isMobileMenuOpen ? (
            <X className="h-6 w-6" aria-hidden="true" />
          ) : (
            <Menu className="h-6 w-6" aria-hidden="true" />
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <nav
          id="mobile-menu"
          className="md:hidden border-t bg-white"
          role="navigation"
          aria-label="Mobile navigation"
        >
          <div className="px-4 py-3 space-y-2">
            <Link
              href="#how-it-works"
              className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-arbor-primary hover:bg-gray-50 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-arbor-primary"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              How It Works
            </Link>
            <Link
              href="#faq"
              className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-arbor-primary hover:bg-gray-50 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-arbor-primary"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              FAQ
            </Link>
          </div>
        </nav>
      )}
    </header>
  );
}
