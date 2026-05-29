"use client";

import { useEffect, useState } from "react";

// 1. Update the interface to include the new data types
interface PlayerProjection {
  batter_name: string;
  total_batted_balls: number;
  xwOBA: number;
  max_exit_velocity: number;
  hard_hit_rate: number;
  home_runs: number;
  projected_ros_hrs: number;
  projected_total_hrs: number;
}

export default function Dashboard() {
  const [data, setData] = useState<PlayerProjection[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/projections?limit=400")
      .then((res) => res.json())
      .then((json) => {
        setData(json.data);
        setLoading(false);
      })
      .catch((err) => console.error("Failed to fetch API:", err));
  }, []);

  const filteredData = data.filter((player) =>
    player.batter_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <main className="min-h-screen bg-gray-50 p-8 text-gray-900">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 border-b pb-4 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-gray-900">
              2026 MLB Home Run Projections
            </h1>
            <p className="text-gray-500 mt-2 text-lg">
              Powered by XGBoost & Advanced Statcast Metrics
            </p>
          </div>
          
          <div className="w-72">
            <input
              type="text"
              placeholder="Search for a player..."
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </header>

        {loading ? (
          <div className="flex justify-center py-20 text-xl font-semibold text-blue-600 animate-pulse">
            Crunching 2026 Statcast Data... This may take a minute.
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div className="max-h-[75vh] overflow-y-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-800 text-white font-semibold uppercase text-xs sticky top-0 shadow-md z-10">
                  <tr>
                    <th className="px-6 py-4">Player</th>
                    <th className="px-6 py-4 text-blue-300">xwOBA</th>
                    <th className="px-6 py-4 text-purple-300">Max EV</th>
                    <th className="px-6 py-4 text-purple-300">Hard Hit %</th>
                    <th className="px-6 py-4 border-l border-slate-700">Current HRs</th>
                    <th className="px-6 py-4 text-orange-400 font-bold">Proj ROS HRs</th>
                    <th className="px-6 py-4 bg-slate-900 text-green-400 font-bold text-base">End of Year Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filteredData.map((player, idx) => (
                      <tr key={idx} className="hover:bg-blue-50 transition-colors">
                        <td className="px-6 py-4 font-bold text-gray-900 text-base">
                          {player.batter_name}
                        </td>
                        <td className="px-6 py-4 font-semibold text-blue-600">
                          {player.xwOBA.toFixed(3)}
                        </td>
                        <td className="px-6 py-4 text-purple-700 font-medium">
                          {player.max_exit_velocity.toFixed(1)} mph
                        </td>
                        <td className="px-6 py-4 text-purple-700 font-medium">
                          {(player.hard_hit_rate * 100).toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 border-l border-gray-200 text-lg">
                          {player.home_runs}
                        </td>
                        <td className="px-6 py-4 font-bold text-orange-600 text-lg">
                          +{player.projected_ros_hrs.toFixed(1)}
                        </td>
                        <td className="px-6 py-4 font-black text-green-600 text-xl bg-gray-50">
                          {player.projected_total_hrs.toFixed(1)}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}