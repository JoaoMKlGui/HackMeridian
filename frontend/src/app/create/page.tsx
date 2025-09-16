"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function CreatePage() {
  const [payTopInputs, setPayTopInputs] = useState([{ percentage: "" }]);
  const [entryFee, setEntryFee] = useState("");
  const [competitionDomain, setCompetitionDomain] = useState("gymrats.com");
  const [competitionId, setCompetitionId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const addPayTopInput = () => {
    setPayTopInputs([...payTopInputs, { percentage: "" }]);
  };

  const removePayTopInput = () => {
    if (payTopInputs.length > 1) {
      setPayTopInputs(payTopInputs.slice(0, -1));
    }
  };

  const updatePayTopInput = (index: number, value: string) => {
    const newInputs = [...payTopInputs];
    newInputs[index].percentage = value;
    setPayTopInputs(newInputs);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const totalPercentage = payTopInputs.reduce(
      (acc, input) => acc + (parseFloat(input.percentage) || 0),
      0
    );

    if (totalPercentage !== 100) {
      setError("The sum of percentages must be 100.");
    } else {
      setError(null);
      // Handle successful submission
      console.log("Form submitted successfully");
      const poolId = "123"; // Replace with actual pool ID from backend
      const competitionLink = `${competitionDomain}/${competitionId}`;
      router.push(
        `/invite/${poolId}?entryFee=${entryFee}&competitionLink=${encodeURIComponent(
          competitionLink
        )}`
      );
    }
  };

  return (
    <main className="mt-[100px] flex min-h-[calc(100vh-100px)] justify-center p-2">
      <div className="w-full max-w-2xl bg-gradient-to-br ">
        <h1 className="text-3xl font-bold text-center mb-8 bg-gradient-to-r from-primary-pink to-primary-blue bg-clip-text text-transparent">
          CREATE
        </h1>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="flex gap-8">
            {/* Left Column for main inputs */}
            <div className="flex-1 space-y-6">
              {/* Start Date */}
              <div className="flex items-center gap-4">
                <label className="text-lg font-semibold text-gray-700 w-32">
                  START DATE:
                </label>
                <input type="date" className="flex-1 apple-input" />
              </div>

              {/* End Date */}
              <div className="flex items-center gap-4">
                <label className="text-lg font-semibold text-gray-700 w-32">
                  END DATE:
                </label>
                <input type="date" className="flex-1 apple-input" />
              </div>

              {/* Entry Fee */}
              <div className="flex items-center gap-4">
                <label className="text-lg font-semibold text-gray-700 w-32">
                  ENTRY FEE:
                </label>
                <input
                  type="number"
                  placeholder="XLM"
                  className="flex-1 apple-input"
                  value={entryFee}
                  onChange={(e) => setEntryFee(e.target.value)}
                />
              </div>

              {/* Competition Link */}
              <div className="flex items-center gap-4">
                <label className="text-lg font-semibold text-gray-700 w-32">
                  COMPETITION LINK:
                </label>
                <div className="flex-1 flex gap-2">
                  <select
                    className="apple-input apple-select"
                    value={competitionDomain}
                    onChange={(e) => setCompetitionDomain(e.target.value)}
                  >
                    <option value="gymrats.com">gymrats.com</option>
                    <option value="other.com">other.com</option>
                  </select>
                  <input
                    type="text"
                    placeholder="123"
                    className="flex-1 apple-input"
                    value={competitionId}
                    onChange={(e) => setCompetitionId(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Right Column for Pay Top K */}
            <div className="space-y-3">
              <label className="text-lg font-semibold text-gray-700">
                PAYOUTS:
              </label>
              {payTopInputs.map((input, index) => (
                <div key={index} className="flex items-center gap-4">
                  <span className="text-gray-600">{index + 1}º:</span>
                  <input
                    type="text"
                    placeholder="100%"
                    value={input.percentage}
                    onChange={(e) => updatePayTopInput(index, e.target.value)}
                    className="w-24 apple-input"
                  />
                  {index === payTopInputs.length - 1 && (
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={addPayTopInput}
                        className="w-10 h-10 bg-transparent text-gray-700 rounded-full font-bold text-xl hover:bg-gray-100 transition-colors"
                      >
                        +
                      </button>
                      {payTopInputs.length > 1 && (
                        <button
                          type="button"
                          onClick={removePayTopInput}
                          className="w-10 h-10 bg-transparent text-gray-700 rounded-full font-bold text-xl hover:bg-gray-100 transition-colors"
                        >
                          -
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            </div>
          </div>

          {/* Create Button Centered */}
          <div className="flex justify-center pt-6">
            <button
              type="submit"
              className="btn btn-primary hero-button w-fit"
            >
              Create Pool
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
