import Link from "next/link";
import { Leaf } from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300" role="contentinfo">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <Leaf className="h-6 w-6 text-arbor-accent" aria-hidden="true" />
              <span className="text-lg font-bold text-white">Arbor Energy</span>
            </Link>
            <p className="text-sm text-gray-400 max-w-md">
              AI-powered energy plan recommendations to help you save money,
              go green, and find the perfect plan for your needs.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Quick Links
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/#get-started"
                  className="text-sm hover:text-white transition-colors"
                >
                  Get Started
                </Link>
              </li>
              <li>
                <Link
                  href="/#how-it-works"
                  className="text-sm hover:text-white transition-colors"
                >
                  How It Works
                </Link>
              </li>
              <li>
                <Link
                  href="/#faq"
                  className="text-sm hover:text-white transition-colors"
                >
                  FAQ
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Legal
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/privacy"
                  className="text-sm hover:text-white transition-colors"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <a
                  href="mailto:support@arbor-energy.com"
                  className="text-sm hover:text-white transition-colors"
                >
                  Contact Us
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-400">
            &copy; {currentYear} Arbor Energy. All rights reserved.
          </p>
          <p className="text-xs text-gray-500">
            GDPR & CCPA Compliant
          </p>
        </div>
      </div>
    </footer>
  );
}
