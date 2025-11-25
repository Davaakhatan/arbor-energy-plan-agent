"use client";

import { Leaf } from "lucide-react";
import Link from "next/link";

export function Header() {
  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2">
          <Leaf className="h-8 w-8 text-arbor-primary" />
          <span className="text-xl font-bold text-gray-900">Arbor Energy</span>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          <Link
            href="#how-it-works"
            className="text-sm font-medium text-gray-600 hover:text-arbor-primary transition-colors"
          >
            How It Works
          </Link>
          <Link
            href="#faq"
            className="text-sm font-medium text-gray-600 hover:text-arbor-primary transition-colors"
          >
            FAQ
          </Link>
        </nav>
      </div>
    </header>
  );
}
