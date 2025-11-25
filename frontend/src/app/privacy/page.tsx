import { Header } from "@/components/ui/Header";
import { Footer } from "@/components/ui/Footer";
import { Shield, Lock, Eye, Trash2, Download, Mail } from "lucide-react";
import Link from "next/link";

export const metadata = {
  title: "Privacy Policy | Arbor Energy",
  description: "Learn how Arbor Energy protects your data and privacy.",
};

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      <Header />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <Link
            href="/"
            className="text-arbor-primary hover:underline text-sm"
          >
            &larr; Back to Home
          </Link>
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
        <p className="text-gray-500 mb-8">
          Effective Date: January 27, 2025 | Last Updated: January 27, 2025
        </p>

        {/* Summary Card */}
        <div className="bg-arbor-primary/5 border border-arbor-primary/20 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-arbor-primary mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Privacy at a Glance
          </h2>
          <div className="grid sm:grid-cols-2 gap-4 text-sm">
            <div className="flex items-start gap-2">
              <Lock className="w-4 h-4 text-green-600 mt-0.5" />
              <span><strong>Data Sold:</strong> Never</span>
            </div>
            <div className="flex items-start gap-2">
              <Eye className="w-4 h-4 text-green-600 mt-0.5" />
              <span><strong>Tracking:</strong> None</span>
            </div>
            <div className="flex items-start gap-2">
              <Trash2 className="w-4 h-4 text-green-600 mt-0.5" />
              <span><strong>Deletion:</strong> On request</span>
            </div>
            <div className="flex items-start gap-2">
              <Download className="w-4 h-4 text-green-600 mt-0.5" />
              <span><strong>Your Data:</strong> Exportable</span>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="prose prose-gray max-w-none">
          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Introduction</h2>
            <p className="text-gray-600">
              Arbor Energy Plan Recommendation Agent is committed to protecting your privacy.
              This Privacy Policy explains how we collect, use, store, and protect your
              information when you use our energy plan recommendation service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Information We Collect</h2>

            <h3 className="text-lg font-medium text-gray-800 mt-4 mb-2">Information You Provide</h3>
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 font-medium">Data Type</th>
                    <th className="text-left py-2 font-medium">Purpose</th>
                  </tr>
                </thead>
                <tbody className="text-gray-600">
                  <tr className="border-b">
                    <td className="py-2">Monthly Usage Data (kWh)</td>
                    <td className="py-2">Generate accurate recommendations</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-2">Preference Settings</td>
                    <td className="py-2">Personalize recommendations</td>
                  </tr>
                  <tr>
                    <td className="py-2">Current Plan Details</td>
                    <td className="py-2">Calculate potential savings</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <h3 className="text-lg font-medium text-gray-800 mt-4 mb-2">Information We Do NOT Collect</h3>
            <ul className="list-disc list-inside text-gray-600 space-y-1">
              <li>Personal names or email addresses</li>
              <li>Physical home addresses</li>
              <li>Payment or banking information</li>
              <li>Social security or government IDs</li>
              <li>Device fingerprints or tracking cookies</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">How We Use Your Information</h2>
            <div className="space-y-3 text-gray-600">
              <p><strong>1. Generate Recommendations:</strong> Your usage data and preferences are used to calculate and rank energy plans.</p>
              <p><strong>2. Calculate Savings:</strong> We compare your current plan costs against available alternatives.</p>
              <p><strong>3. Improve Service:</strong> Aggregated, anonymized patterns help us improve our algorithms.</p>
            </div>

            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
              <h4 className="font-medium text-red-800 mb-2">We Do NOT Use Your Data For:</h4>
              <ul className="list-disc list-inside text-red-700 text-sm space-y-1">
                <li>Marketing or advertising</li>
                <li>Selling to third parties</li>
                <li>Building user profiles for other purposes</li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Security</h2>
            <div className="bg-gray-50 rounded-lg p-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 font-medium">Layer</th>
                    <th className="text-left py-2 font-medium">Protection</th>
                  </tr>
                </thead>
                <tbody className="text-gray-600">
                  <tr className="border-b">
                    <td className="py-2">Transport</td>
                    <td className="py-2">TLS 1.3 encryption</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-2">Database</td>
                    <td className="py-2">Encrypted at rest</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-2">Application</td>
                    <td className="py-2">Input validation, SQL injection prevention</td>
                  </tr>
                  <tr>
                    <td className="py-2">Infrastructure</td>
                    <td className="py-2">Rate limiting (60 req/min)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Rights (GDPR)</h2>
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-1">Right to Access</h4>
                <p className="text-sm text-gray-600">Request a copy of all data we hold about you.</p>
              </div>
              <div className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-1">Right to Rectification</h4>
                <p className="text-sm text-gray-600">Correct inaccurate data or update your information.</p>
              </div>
              <div className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-1">Right to Erasure</h4>
                <p className="text-sm text-gray-600">Request permanent deletion of all your data.</p>
              </div>
              <div className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-1">Right to Portability</h4>
                <p className="text-sm text-gray-600">Receive your data in a machine-readable format (JSON).</p>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Retention</h2>
            <div className="bg-gray-50 rounded-lg p-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 font-medium">Data Type</th>
                    <th className="text-left py-2 font-medium">Retention Period</th>
                  </tr>
                </thead>
                <tbody className="text-gray-600">
                  <tr className="border-b">
                    <td className="py-2">Customer Usage Data</td>
                    <td className="py-2">Until deletion requested or 2 years inactive</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-2">Preferences</td>
                    <td className="py-2">Until deletion requested</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-2">Cached Recommendations</td>
                    <td className="py-2">1 hour</td>
                  </tr>
                  <tr>
                    <td className="py-2">Access Logs</td>
                    <td className="py-2">24 hours</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Us</h2>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <p className="flex items-center gap-2 text-gray-600">
                <Mail className="w-4 h-4" />
                <span><strong>General:</strong> support@arbor-energy.com</span>
              </p>
              <p className="flex items-center gap-2 text-gray-600">
                <Shield className="w-4 h-4" />
                <span><strong>Privacy:</strong> privacy@arbor-energy.com</span>
              </p>
              <p className="flex items-center gap-2 text-gray-600">
                <Lock className="w-4 h-4" />
                <span><strong>Security:</strong> security@arbor-energy.com</span>
              </p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Regulatory Compliance</h2>
            <p className="text-gray-600">
              This Privacy Policy is designed to comply with:
            </p>
            <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
              <li><strong>GDPR</strong> (General Data Protection Regulation) - EU</li>
              <li><strong>CCPA</strong> (California Consumer Privacy Act) - California, US</li>
              <li><strong>LGPD</strong> (Lei Geral de Proteção de Dados) - Brazil</li>
            </ul>
          </section>
        </div>
      </div>

      <Footer />
    </main>
  );
}
