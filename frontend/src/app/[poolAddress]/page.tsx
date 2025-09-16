"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useState } from "react";
import { Copy, Check } from "lucide-react";

export default function PoolPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const entryFee = searchParams.get("entryFee");
  const competitionLink = searchParams.get("competitionLink");
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (typeof params.poolAddress === "string") {
      navigator.clipboard.writeText(params.poolAddress);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-2xl rounded-2xl bg-white/50 p-12 text-center shadow-lg backdrop-blur-lg">
        <h1 className="font-sans text-3xl font-semibold text-gray-800">
          Pay{" "}
          <span className="bg-gradient-to-r from-pink-500 to-blue-500 bg-clip-text text-transparent">
            {entryFee} XLM
          </span>{" "}
          to this address to enter:
        </h1>
        <div className="mt-4 flex items-center justify-center gap-4">
          <p className="rounded-lg bg-gray-100 p-4 font-mono text-2xl text-gray-700">
            0E1A34C1903CFA657923FAA0B23432CE 
          </p>
          <button onClick={handleCopy} className="bg-transparent border-none">
            {copied ? <Check size={20} /> : <Copy size={20} />}
          </button>
        </div>
        {competitionLink && (
          <div className="mt-6 text-lg text-gray-600">
            Competition token:{" "}
            <a
              href={`https://${competitionLink}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {competitionLink}
            </a>
          </div>
        )}
        <div className="mt-8 flex items-center justify-center">
          <label
            htmlFor="username"
            className="mr-3 text-lg font-medium text-gray-700"
          >
            Username at competition:
          </label>
          <input
            id="username"
            type="text"
            placeholder="Your username"
            className="w-64 rounded-lg border border-gray-300 bg-white px-4 py-2 text-lg text-gray-900 shadow-sm transition-shadow duration-200 ease-in-out placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
        </div>
        <div className="mt-8">
          <button
            disabled
            className="rounded-lg bg-gray-200 px-6 py-3 text-lg font-semibold text-gray-500"
          >
            Waiting for payment
          </button>
        </div>
      </div>
    </main>
  );
}
