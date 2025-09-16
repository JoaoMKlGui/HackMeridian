"use client";

import { useState } from "react";
import { ConnectWallet } from "../Buttons/ConnectWallet";
import Link from "next/link";

export const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const NAV_LINKS = [{ name: "Pools", href: "/pools" }];

  return (
    <header className="fixed text-3xl h-25 top-0 left-0 w-full z-50 bg-[#F2EEFF60] border-b border-black/10">
      <nav className="flex items-center justify-end px-4 md:px-12 h-full">
        {/* Mobile Nav Toggle */}
        <>
          <div className="md:hidden absolute right-4 top-1/2 -translate-y-1/2 z-50">
            <div>ok</div>
            <span className="text-primary-pink">NOT</span>
            <span className="text-primary-blue">Gambling</span>
            <button
              className="btn btn-circle h-14 w-14 bg-[#232136]"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open menu"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
              {NAV_LINKS.map((link) => (
                <Link key={link.name} href={link.href}>
                  {link.name}
                </Link>
              ))}
            </button>
          </div>
          {mobileMenuOpen && (
            <div
              className="fixed inset-0 z-50 bg-[#0f1016] flex flex-col items-center justify-start pt-24 transition-all duration-300 ease-out animate-navbar-slide"
              onClick={() => setMobileMenuOpen(false)}
            >
              <ConnectWallet className="mt-10 w-[90%] flex justify-center" />
            </div>
          )}
        </>
        {/* Right Side Controls */}
        <div className="flex items-center gap-3">
          {/* Connect Wallet Button */}
          <ConnectWallet className="hidden md:block" />
        </div>
      </nav>
    </header>
  );
};
