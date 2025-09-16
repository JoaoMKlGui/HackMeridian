"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useState } from "react";
import { Copy, Check } from "lucide-react";

export default function PoolPage() {
  const { poolId } = useParams();
  const searchParams = useSearchParams();
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const url = `https://notgambling.com/${poolId}`;
    const localUrl = `http://localhost:3000/${poolId}?entryFee=${searchParams.get(
      "entryFee"
    )}&competitionLink=${searchParams.get("competitionLink")}`;
    navigator.clipboard.writeText(localUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <main className="flex flex-col min-h-screen justify-center items-center p-4 -mt-20">
      <div className="text-center">
        <p className="text-lg font-semibold text-gray-600 mb-2">invite:</p>
        <div className="flex items-center gap-4">
          <a
            href={`/${poolId}?entryFee=${searchParams.get(
              "entryFee"
            )}&competitionLink=${searchParams.get("competitionLink")}`}
            className="text-5xl font-bold bg-gradient-to-r from-pink-500 to-blue-500 bg-clip-text text-transparent pb-2"
          >
            notgambling.com/{poolId}
          </a>
          <button
            onClick={handleCopy}
            className="bg-transparent border-none"
          >
            {copied ? <Check size={20} /> : <Copy size={20} />}
          </button>
        </div>
      </div>
    </main>
  );
}
