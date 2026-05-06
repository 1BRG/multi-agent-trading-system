"use client";

import React, { useState, useEffect } from "react";
import { Strategy, getStrategies, generateAiStrategy } from "../../lib/strategy";

export default function StrategyManager() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load existing strategies on mount
  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const data = await getStrategies();
      setStrategies(data);
    } catch (err: any) {
      console.error("Failed to fetch strategies", err);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const newStrategy = await generateAiStrategy(prompt);
      // Add the new strategy to the top of the list
      setStrategies((prev) => [newStrategy, ...prev]);
      setPrompt(""); // Clear the input
    } catch (err: any) {
      setError(err.message || "Failed to generate strategy. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-8">
      {/* --- AI Prompt Section --- */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">AI Strategy Builder</h2>
        <p className="text-sm text-gray-600 mb-4">
          Describe the trading strategy you want to build. The AI will translate your idea into strict, backtestable rules.
        </p>

        <form onSubmit={handleGenerate} className="space-y-4">
          <textarea
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
            placeholder="e.g., Build a weekly momentum strategy that holds the top 5 highest conviction tech stocks, equal weighted."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
          />
          
          {error && <div className="text-red-600 text-sm">{error}</div>}

          <button
            type="submit"
            disabled={isLoading || !prompt.trim()}
            className="w-full bg-blue-600 text-white font-medium py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {isLoading ? "Generating Ruleset..." : "Generate Deterministic Ruleset"}
          </button>
        </form>
      </div>

      {/* --- Generated Strategies List --- */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Your Saved Strategies</h3>
        {strategies.length === 0 ? (
          <p className="text-gray-500 text-sm">No strategies generated yet.</p>
        ) : (
          <div className="space-y-4">
            {strategies.map((strategy) => (
              <div key={strategy.id} className="bg-gray-50 p-5 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-lg text-gray-900">{strategy.name}</h4>
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full uppercase tracking-wider font-semibold">
                    {strategy.source}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-4">{strategy.description}</p>
                
                {/* The "Frozen Rule" visualization: Showing the hardcoded JSON to the user */}
                <div className="bg-gray-900 rounded-md p-4 overflow-x-auto">
                  <p className="text-xs text-gray-400 mb-2 uppercase tracking-wide">Deterministic Backtest Config:</p>
                  <pre className="text-green-400 text-sm font-mono">
                    {JSON.stringify(strategy.config, null, 2)}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}