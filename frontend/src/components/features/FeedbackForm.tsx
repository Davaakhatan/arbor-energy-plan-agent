"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Star, ThumbsUp, ThumbsDown, Check } from "lucide-react";
import { feedbackApi } from "@/lib/api";
import type { FeedbackCreate, Recommendation } from "@/types";

interface FeedbackFormProps {
  customerId: string;
  recommendation: Recommendation;
  onSubmitted?: () => void;
}

export function FeedbackForm({
  customerId,
  recommendation,
  onSubmitted,
}: FeedbackFormProps) {
  const [rating, setRating] = useState<number | null>(null);
  const [wasHelpful, setWasHelpful] = useState<boolean | null>(null);
  const [switchedToPlan, setSwitchedToPlan] = useState<boolean | null>(null);
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (rating === null) {
      setError("Please provide a rating");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const feedbackData: FeedbackCreate = {
        customer_id: customerId,
        plan_id: recommendation.plan.id,
        feedback_type: "recommendation_rating",
        rating,
        was_helpful: wasHelpful ?? undefined,
        switched_to_plan: switchedToPlan ?? undefined,
        comment: comment || undefined,
        metadata: {
          recommendation_id: recommendation.id,
          plan_name: recommendation.plan.name,
        },
      };

      await feedbackApi.submit(feedbackData);
      setIsSubmitted(true);
      onSubmitted?.();
    } catch (err) {
      setError("Failed to submit feedback. Please try again.");
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <Card className="bg-green-50 border-green-200">
        <CardContent className="py-4">
          <div className="flex items-center gap-2 text-green-700">
            <Check className="w-5 h-5" aria-hidden="true" />
            <span>Thank you for your feedback!</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base" id="feedback-title">
          Rate this recommendation
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          aria-labelledby="feedback-title"
          className="space-y-4"
        >
          {/* Star Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              How would you rate this recommendation?
            </label>
            <div
              className="flex gap-1"
              role="radiogroup"
              aria-label="Rating from 1 to 5 stars"
            >
              {[1, 2, 3, 4, 5].map((value) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setRating(value)}
                  className={`p-1 rounded transition-colors ${
                    rating !== null && value <= rating
                      ? "text-yellow-400"
                      : "text-gray-300 hover:text-yellow-300"
                  }`}
                  role="radio"
                  aria-checked={rating === value}
                  aria-label={`${value} star${value !== 1 ? "s" : ""}`}
                >
                  <Star
                    className="w-8 h-8"
                    fill={rating !== null && value <= rating ? "currentColor" : "none"}
                    aria-hidden="true"
                  />
                </button>
              ))}
            </div>
          </div>

          {/* Helpful? */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Was this recommendation helpful?
            </label>
            <div className="flex gap-2">
              <Button
                type="button"
                variant={wasHelpful === true ? "primary" : "outline"}
                size="sm"
                onClick={() => setWasHelpful(true)}
                aria-pressed={wasHelpful === true}
              >
                <ThumbsUp className="w-4 h-4 mr-1" aria-hidden="true" />
                Yes
              </Button>
              <Button
                type="button"
                variant={wasHelpful === false ? "primary" : "outline"}
                size="sm"
                onClick={() => setWasHelpful(false)}
                aria-pressed={wasHelpful === false}
              >
                <ThumbsDown className="w-4 h-4 mr-1" aria-hidden="true" />
                No
              </Button>
            </div>
          </div>

          {/* Did you switch? */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Did you switch to this plan?
            </label>
            <div className="flex gap-2">
              <Button
                type="button"
                variant={switchedToPlan === true ? "primary" : "outline"}
                size="sm"
                onClick={() => setSwitchedToPlan(true)}
                aria-pressed={switchedToPlan === true}
              >
                Yes, I switched
              </Button>
              <Button
                type="button"
                variant={switchedToPlan === false ? "primary" : "outline"}
                size="sm"
                onClick={() => setSwitchedToPlan(false)}
                aria-pressed={switchedToPlan === false}
              >
                No
              </Button>
            </div>
          </div>

          {/* Comment */}
          <div>
            <label
              htmlFor="feedback-comment"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Additional comments (optional)
            </label>
            <textarea
              id="feedback-comment"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-arbor-primary focus:border-transparent resize-none"
              rows={3}
              placeholder="Tell us more about your experience..."
              maxLength={2000}
            />
          </div>

          {error && (
            <div
              className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600"
              role="alert"
              aria-live="assertive"
            >
              {error}
            </div>
          )}

          <Button
            type="submit"
            isLoading={isSubmitting}
            loadingText="Submitting..."
            disabled={rating === null}
            className="w-full"
          >
            Submit Feedback
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
