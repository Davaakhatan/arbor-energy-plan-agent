import { Header } from "@/components/ui/Header";
import { Footer } from "@/components/ui/Footer";
import { Hero } from "@/components/features/Hero";
import { RecommendationFlow } from "@/components/features/RecommendationFlow";
import { HowItWorks } from "@/components/features/HowItWorks";
import { FAQ } from "@/components/features/FAQ";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      <Header />
      <Hero />
      <RecommendationFlow />
      <HowItWorks />
      <FAQ />
      <Footer />
    </main>
  );
}
