"use client";

import { useState } from "react";

export default function CreatePage() {
  const [payTopInputs, setPayTopInputs] = useState([{ percentage: "" }]);

  const addPayTopInput = () => {
    setPayTopInputs([...payTopInputs, { percentage: "" }]);
  };

  const updatePayTopInput = (index: number, value: string) => {
    const newInputs = [...payTopInputs];
    newInputs[index].percentage = value;
    setPayTopInputs(newInputs);
  };

  return (
    <main className="mt-[100px] flex min-h-[calc(100vh-100px)] justify-center p-2">
      <div className="w-full max-w-2xl bg-gradient-to-br ">
        <h1 className="text-3xl font-bold text-center mb-8 bg-gradient-to-r from-primary-pink to-primary-blue bg-clip-text text-transparent">
          CREATE
        </h1>

        <form className="space-y-6 flex flex-col gap-4">
          {/* Start Date */}
          <div className="flex items-center gap-4">
            <label className="text-lg font-semibold text-gray-700 w-32">
              START DATE:
            </label>
            <input
              type="date"
              className="flex-1 p-3 bg-white/70 border-2 border-purple-200 rounded-md focus:border-primary-pink focus:outline-none focus:bg-white/90 transition-all"
            />
          </div>

          {/* End Date */}
          <div className="flex items-center gap-4">
            <label className="text-lg font-semibold text-gray-700 w-32">
              END DATE:
            </label>
            <input
              type="date"
              className="flex-1 p-3 bg-white/70 border-2 border-purple-200 rounded-md focus:border-primary-pink focus:outline-none focus:bg-white/90 transition-all"
            />
          </div>

          {/* Entry Fee */}
          <div className="flex items-center gap-4">
            <label className="text-lg font-semibold text-gray-700 w-32">
              ENTRY FEE:
            </label>
            <input
              type="number"
              placeholder="XLM"
              className="flex-1 p-3 bg-white/70 border-2 border-purple-200 rounded-md focus:border-primary-pink focus:outline-none focus:bg-white/90 transition-all"
            />
          </div>

          {/* Competition Link */}
          <div className="flex items-center gap-4">
            <label className="text-lg font-semibold text-gray-700 w-32">
              COMPETITION LINK:
            </label>
            <div className="flex-1 flex gap-2">
              <select className="p-3 bg-white/70 border-2 border-purple-200 rounded-md focus:border-primary-pink focus:outline-none focus:bg-white/90 transition-all">
                <option value="gymrats.com">gymrats.com</option>
                <option value="other.com">other.com</option>
              </select>
              <input
                type="text"
                placeholder="(139"
                className="flex-1 p-3 bg-white/70 border-2 border-purple-200 rounded-md focus:border-primary-pink focus:outline-none focus:bg-white/90 transition-all"
              />
            </div>
          </div>

          {/* Pay Top K */}
          <div className="space-y-3">
            <label className="text-lg font-semibold text-gray-700">
              PAY TOP
            </label>
            {payTopInputs.map((input, index) => (
              <div key={index} className="flex items-center gap-4 ml-8">
                <span className="text-gray-600">{index + 1}º:</span>
                <input
                  type="text"
                  placeholder="100%"
                  value={input.percentage}
                  onChange={(e) => updatePayTopInput(index, e.target.value)}
                  className="w-24 p-3 bg-white/70 border-2 border-purple-200 rounded-md focus:border-primary-pink focus:outline-none focus:bg-white/90 transition-all"
                />
                {index === payTopInputs.length - 1 && (
                  <button
                    type="button"
                    onClick={addPayTopInput}
                    className="w-10 h-10 bg-primary-pink text-black rounded-full font-bold text-xl hover:bg-opacity-80 transition-colors"
                  >
                    +
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Create Button */}
          <div className="flex justify-end pt-6">
            <button type="submit" className="btn btn-primary px-8">
              CREATE
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
