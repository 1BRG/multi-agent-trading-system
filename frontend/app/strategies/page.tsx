import StrategyManager from "../../components/strategies/StrategyManager";

export default function StrategiesPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Strategy Lab</h1>
        <p className="text-gray-600 mb-8">
          Design deterministic trading rulesets using AI, ready for historical backtesting.
        </p>
        
        {}
        <StrategyManager />
      </div>
    </div>
  );
}