import { Header } from "@/components/ui/Header";
import { Hero } from "@/components/features/Hero";
import { RecommendationFlow } from "@/components/features/RecommendationFlow";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      <Header />
      <Hero />
      <RecommendationFlow />
    </main>
  );
}
