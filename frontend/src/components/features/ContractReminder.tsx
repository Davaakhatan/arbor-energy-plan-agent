"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  Bell,
  Calendar,
  Mail,
  AlertTriangle,
  Check,
  X,
  Clock,
} from "lucide-react";

interface ContractReminderProps {
  contractEndDate?: string;
  planName?: string;
  providerName?: string;
  earlyTerminationFee?: number;
}

interface ReminderOption {
  id: string;
  label: string;
  daysBefore: number;
}

const REMINDER_OPTIONS: ReminderOption[] = [
  { id: "30days", label: "30 days before", daysBefore: 30 },
  { id: "14days", label: "14 days before", daysBefore: 14 },
  { id: "7days", label: "7 days before", daysBefore: 7 },
  { id: "1day", label: "1 day before", daysBefore: 1 },
];

export function ContractReminder({
  contractEndDate,
  planName,
  providerName,
  earlyTerminationFee,
}: ContractReminderProps) {
  const [email, setEmail] = useState("");
  const [selectedReminders, setSelectedReminders] = useState<string[]>(["30days", "7days"]);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [showForm, setShowForm] = useState(false);

  // Calculate days until contract end
  const daysUntilEnd = contractEndDate
    ? Math.ceil(
        (new Date(contractEndDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
      )
    : null;

  // Check if there's a saved reminder in localStorage
  useEffect(() => {
    const savedReminder = localStorage.getItem("contractReminder");
    if (savedReminder) {
      const { email: savedEmail, reminders } = JSON.parse(savedReminder);
      setEmail(savedEmail);
      setSelectedReminders(reminders);
      setIsSubscribed(true);
    }
  }, []);

  const toggleReminder = (id: string) => {
    setSelectedReminders((prev) =>
      prev.includes(id) ? prev.filter((r) => r !== id) : [...prev, id]
    );
  };

  const handleSubscribe = () => {
    if (!email || selectedReminders.length === 0) return;

    // In a real app, this would call an API to set up email reminders
    // For now, we'll save to localStorage and show a success message
    const reminderData = {
      email,
      reminders: selectedReminders,
      contractEndDate,
      planName,
      providerName,
      createdAt: new Date().toISOString(),
    };

    localStorage.setItem("contractReminder", JSON.stringify(reminderData));
    setIsSubscribed(true);
    setShowForm(false);

    // Also create a calendar event download
    downloadCalendarEvent();
  };

  const handleUnsubscribe = () => {
    localStorage.removeItem("contractReminder");
    setIsSubscribed(false);
    setEmail("");
    setSelectedReminders(["30days", "7days"]);
  };

  const downloadCalendarEvent = () => {
    if (!contractEndDate) return;

    const endDate = new Date(contractEndDate);
    const reminderDate = new Date(endDate);
    reminderDate.setDate(reminderDate.getDate() - 30);

    const formatDate = (date: Date) => {
      return date.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
    };

    const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Arbor Energy//Contract Reminder//EN
BEGIN:VEVENT
UID:${Date.now()}@arbor-energy.com
DTSTAMP:${formatDate(new Date())}
DTSTART:${formatDate(reminderDate)}
DTEND:${formatDate(reminderDate)}
SUMMARY:Energy Contract Ending Soon - ${planName || "Your Plan"}
DESCRIPTION:Your energy contract${providerName ? ` with ${providerName}` : ""} ends on ${endDate.toLocaleDateString()}. Consider reviewing new plans to avoid auto-renewal or early termination fees.${earlyTerminationFee ? ` Early termination fee: $${earlyTerminationFee}` : ""}
BEGIN:VALARM
TRIGGER:-P7D
ACTION:DISPLAY
DESCRIPTION:Energy contract ending in 7 days
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Energy contract ends tomorrow
END:VALARM
END:VEVENT
END:VCALENDAR`;

    const blob = new Blob([icsContent], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `contract-reminder-${contractEndDate}.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Don't show if no contract end date
  if (!contractEndDate) {
    return null;
  }

  const endDate = new Date(contractEndDate);
  const isExpired = daysUntilEnd !== null && daysUntilEnd <= 0;
  const isUrgent = daysUntilEnd !== null && daysUntilEnd > 0 && daysUntilEnd <= 14;
  const isApproaching = daysUntilEnd !== null && daysUntilEnd > 14 && daysUntilEnd <= 30;

  return (
    <Card className={isUrgent ? "border-orange-300" : isApproaching ? "border-yellow-300" : ""}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className={`w-5 h-5 ${isUrgent ? "text-orange-500" : "text-arbor-primary"}`} aria-hidden="true" />
          Contract Reminder
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Contract Status */}
        <div className={`p-4 rounded-lg ${
          isExpired ? "bg-green-50 border border-green-200" :
          isUrgent ? "bg-orange-50 border border-orange-200" :
          isApproaching ? "bg-yellow-50 border border-yellow-200" :
          "bg-gray-50 border border-gray-200"
        }`}>
          <div className="flex items-start gap-3">
            {isExpired ? (
              <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
            ) : isUrgent ? (
              <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
            ) : (
              <Clock className="w-5 h-5 text-gray-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
            )}
            <div>
              <p className={`font-medium ${
                isExpired ? "text-green-800" :
                isUrgent ? "text-orange-800" :
                isApproaching ? "text-yellow-800" :
                "text-gray-800"
              }`}>
                {isExpired
                  ? "Contract has ended - no termination fee!"
                  : `${daysUntilEnd} days until contract ends`}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {planName && <span className="font-medium">{planName}</span>}
                {planName && providerName && " with "}
                {providerName && <span>{providerName}</span>}
                {" ends on "}
                <span className="font-medium">
                  {endDate.toLocaleDateString("en-US", {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </span>
              </p>
              {earlyTerminationFee && !isExpired && (
                <p className="text-sm text-orange-700 mt-2">
                  Early termination fee: ${earlyTerminationFee}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Subscription Status */}
        {isSubscribed ? (
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-600" aria-hidden="true" />
              <span className="text-sm text-green-700">
                Reminders set for {email}
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleUnsubscribe}
              className="text-gray-500 hover:text-red-500"
            >
              <X className="w-4 h-4" aria-hidden="true" />
            </Button>
          </div>
        ) : showForm ? (
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            {/* Email Input */}
            <div>
              <label htmlFor="reminder-email" className="block text-sm font-medium text-gray-700 mb-1">
                Email for reminders
              </label>
              <input
                id="reminder-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-arbor-primary focus:border-transparent"
              />
            </div>

            {/* Reminder Options */}
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">
                Remind me:
              </p>
              <div className="grid grid-cols-2 gap-2">
                {REMINDER_OPTIONS.map((option) => (
                  <label
                    key={option.id}
                    className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition-colors ${
                      selectedReminders.includes(option.id)
                        ? "border-arbor-primary bg-arbor-light"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedReminders.includes(option.id)}
                      onChange={() => toggleReminder(option.id)}
                      className="w-4 h-4 text-arbor-primary rounded focus:ring-arbor-primary"
                    />
                    <span className="text-sm">{option.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button
                onClick={handleSubscribe}
                disabled={!email || selectedReminders.length === 0}
                className="flex-1"
              >
                <Mail className="w-4 h-4 mr-2" aria-hidden="true" />
                Set Reminders
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              variant="outline"
              onClick={() => setShowForm(true)}
              className="flex-1"
            >
              <Mail className="w-4 h-4 mr-2" aria-hidden="true" />
              Set Email Reminders
            </Button>
            <Button
              variant="outline"
              onClick={downloadCalendarEvent}
              className="flex-1"
            >
              <Calendar className="w-4 h-4 mr-2" aria-hidden="true" />
              Add to Calendar
            </Button>
          </div>
        )}

        {/* Tips */}
        {!isExpired && (
          <div className="text-xs text-gray-500 space-y-1">
            <p>
              <strong>Tip:</strong> Most contracts auto-renew 30-60 days before expiration.
            </p>
            {isApproaching && (
              <p className="text-yellow-700">
                Now is a great time to start comparing new plans!
              </p>
            )}
            {isUrgent && (
              <p className="text-orange-700">
                Act soon to avoid auto-renewal at potentially higher rates.
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
