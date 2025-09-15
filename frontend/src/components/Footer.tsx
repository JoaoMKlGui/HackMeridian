"use client";

import Link from "next/link";
import { FileText } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-surface-page px-4 py-6 md:px-12">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 lg:flex-row">
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-6">
            <Link href="/" className="hover:text-primary/80 transition-colors">
              Home
            </Link>
          </div>

          <div className="text-center">
            <p>©2025 Not Gambling. All rights reserved.</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Link
            href="https://docs.notgambling.finance"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-primary transition-colors"
            aria-label="Documentation"
          >
            <FileText size={20} />
          </Link>
        </div>
      </div>
    </footer>
  );
};
