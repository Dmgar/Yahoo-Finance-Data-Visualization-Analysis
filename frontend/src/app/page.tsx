"use client";

import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import { TrendingUp, TrendingDown, Activity, DollarSign, RefreshCw, BarChart2, Search, Bell, Menu, ArrowUpRight, ArrowDownRight } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedPair, setSelectedPair] = useState("EURUSD");
  const [selectedPeriod, setSelectedPeriod] = useState("3m");
  const [showNotifications, setShowNotifications] = useState(false);
  
  const pairs = [
    { id: "EURUSD", name: "EUR/USD", region: "EU/US" },
    { id: "GBPUSD", name: "GBP/USD", region: "UK/US" },
    { id: "USDJPY", name: "USD/JPY", region: "US/JP" },
    { id: "AUDUSD", name: "AUD/USD", region: "AU/US" },
    { id: "USDCHF", name: "USD/CHF", region: "US/CH" }
  ];

  const fetchData = async (pair: string, period: string) => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pair, period: period, window: 20, indicators: true })
      });
      const json = await res.json();
      if (json.status === "success") {
        setData(json);
      }
    } catch (error) {
      console.error("Failed to fetch data:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData(selectedPair, selectedPeriod);
  }, [selectedPair, selectedPeriod]);

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-cyan-500/30">
      
      {/* Navbar Superior */}
      <nav className="glass sticky top-0 z-50 px-6 py-4 flex justify-between items-center border-b-0 border-white/5 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.4)]">
            <Activity className="text-white w-6 h-6" />
          </div>
          <h1 className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-zinc-100 to-zinc-400">
            Forex Volatility
          </h1>
        </div>
        
        <div className="hidden md:flex items-center gap-6">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 group-focus-within:text-cyan-400 transition-colors" />
            <input 
              type="text" 
              placeholder="Search pairs..." 
              className="bg-black/20 border border-white/10 rounded-full py-2 pl-10 pr-4 text-sm outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all w-64 placeholder:text-zinc-600"
            />
          </div>
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-full hover:bg-white/5 transition-colors"
            >
              <Bell className="w-5 h-5 text-zinc-400" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-purple-500 rounded-full shadow-[0_0_8px_rgba(168,85,247,0.8)] animate-pulse"></span>
            </button>
            
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-72 glass rounded-2xl overflow-hidden shadow-2xl border border-white/10 z-50 animate-in fade-in slide-in-from-top-2">
                <div className="p-3 border-b border-white/5 bg-white/5">
                  <h3 className="font-semibold text-sm">Notifications</h3>
                </div>
                <div className="flex flex-col">
                  <div className="p-3 border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer">
                    <p className="text-xs text-cyan-400 font-semibold mb-1">Volatility Alert</p>
                    <p className="text-sm text-zinc-300">EUR/USD ATR has increased by 15% in the last 24h.</p>
                    <p className="text-[10px] text-zinc-500 mt-1">2 mins ago</p>
                  </div>
                  <div className="p-3 hover:bg-white/5 transition-colors cursor-pointer">
                    <p className="text-xs text-purple-400 font-semibold mb-1">System Update</p>
                    <p className="text-sm text-zinc-300">Yahoo Finance real-time data sync completed successfully.</p>
                    <p className="text-[10px] text-zinc-500 mt-1">1 hour ago</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-[1600px] mx-auto w-full grid grid-cols-1 xl:grid-cols-12 gap-6 md:gap-8">
        
        {/* Panel Lateral (Sidebar) */}
        <aside className="xl:col-span-3 flex flex-col gap-6">
          
          <div className="glass rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-cyan-500/10 blur-3xl rounded-full group-hover:bg-cyan-500/20 transition-all duration-700"></div>
            
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-cyan-400" />
                Pairs
              </h2>
              <button 
                onClick={() => fetchData(selectedPair)}
                className="p-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                title="Refresh Data"
              >
                <RefreshCw className={`w-4 h-4 text-zinc-300 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
            
            <div className="flex flex-col gap-3">
              {pairs.map((pair) => (
                <button
                  key={pair.id}
                  onClick={() => setSelectedPair(pair.id)}
                  className={`relative p-4 rounded-2xl flex justify-between items-center transition-all duration-300 overflow-hidden ${
                    selectedPair === pair.id 
                      ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/10 border border-cyan-500/40 shadow-[0_4px_20px_rgba(6,182,212,0.15)]' 
                      : 'bg-black/20 hover:bg-white/5 border border-white/5'
                  }`}
                >
                  {selectedPair === pair.id && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.8)] rounded-l-2xl"></div>
                  )}
                  <div className="flex flex-col text-left pl-2">
                    <span className={`font-bold tracking-wide ${selectedPair === pair.id ? 'text-white' : 'text-zinc-300'}`}>{pair.name}</span>
                    <span className="text-xs text-zinc-500">{pair.region}</span>
                  </div>
                  {selectedPair === pair.id && <Activity className="w-5 h-5 text-cyan-400" />}
                </button>
              ))}
            </div>
          </div>

          {/* Indicadores Técnicos Panel */}
          {data && (
            <div className="glass rounded-3xl p-6">
              <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-purple-400" />
                Technical Analysis
              </h2>
              <div className="space-y-5">
                <div className="p-4 rounded-2xl bg-black/30 border border-white/5">
                  <div className="flex justify-between items-center mb-1">
                    <p className="text-xs text-zinc-400 font-medium">RSI (14)</p>
                    <span className="text-xs px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">Neutral</span>
                  </div>
                  <p className="text-2xl font-mono text-zinc-200">
                    {data.chart_data[data.chart_data.length-1]?.rsi?.toFixed(1) || '--'}
                  </p>
                </div>
                
                <div className="p-4 rounded-2xl bg-black/30 border border-white/5">
                  <div className="flex justify-between items-center mb-1">
                    <p className="text-xs text-zinc-400 font-medium">MACD</p>
                    <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400 border border-green-500/30">Buy Signal</span>
                  </div>
                  <p className="text-xl font-mono text-zinc-200">
                    {data.chart_data[data.chart_data.length-1]?.macd?.toFixed(4) || '--'}
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-black/30 border border-white/5">
                  <p className="text-xs text-zinc-400 font-medium mb-1">Bollinger Band Width</p>
                  <p className="text-xl font-mono text-zinc-200">{data.summary.bb_width_pct !== null ? `${data.summary.bb_width_pct}%` : '--'}</p>
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Área Principal (Gráficos y Tarjetas) */}
        <main className="xl:col-span-9 flex flex-col gap-6 md:gap-8">
          
          {/* Tarjetas de Resumen Numérico */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass rounded-3xl p-6 relative overflow-hidden group hover:-translate-y-1 transition-transform duration-300">
              <div className="absolute -bottom-6 -right-6 w-24 h-24 bg-purple-500/20 blur-2xl rounded-full group-hover:bg-purple-500/30 transition-all"></div>
              <p className="text-sm font-medium text-zinc-400">Current Price</p>
              <div className="flex items-baseline gap-3 mt-2">
                <h3 className="text-4xl font-bold font-mono text-white">
                  {data ? data.summary.price.toFixed(4) : '0.0000'}
                </h3>
              </div>
            </div>
            
            <div className="glass rounded-3xl p-6 relative overflow-hidden group hover:-translate-y-1 transition-transform duration-300">
              <div className="absolute -bottom-6 -right-6 w-24 h-24 bg-cyan-500/20 blur-2xl rounded-full group-hover:bg-cyan-500/30 transition-all"></div>
              <p className="text-sm font-medium text-zinc-400">Total Return ({selectedPeriod.toUpperCase()})</p>
              <div className="flex items-center gap-3 mt-2">
                <h3 className={`text-4xl font-bold font-mono ${data?.summary?.cumulative_return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {data && data.summary.cumulative_return_pct !== null ? `${data.summary.cumulative_return_pct}%` : '--'}
                </h3>
                {data?.summary?.cumulative_return_pct >= 0 ? 
                  <ArrowUpRight className="w-8 h-8 text-green-400 opacity-80" /> : 
                  <ArrowDownRight className="w-8 h-8 text-red-400 opacity-80" />
                }
              </div>
            </div>

            <div className="glass rounded-3xl p-6 relative overflow-hidden group hover:-translate-y-1 transition-transform duration-300">
              <div className="absolute -bottom-6 -right-6 w-24 h-24 bg-blue-500/20 blur-2xl rounded-full group-hover:bg-blue-500/30 transition-all"></div>
              <p className="text-sm font-medium text-zinc-400">Annual Volatility</p>
              <div className="flex items-baseline gap-3 mt-2">
                <h3 className="text-4xl font-bold font-mono text-zinc-100">
                  {data && data.summary.volatility_annual_pct !== null ? `${data.summary.volatility_annual_pct}%` : '--'}
                </h3>
              </div>
            </div>
          </div>

          {/* Gráfico Principal */}
          <div className="glass rounded-3xl p-6 flex-1 min-h-[450px] flex flex-col relative overflow-hidden group">
            <div className="absolute top-0 left-1/4 w-1/2 h-full bg-gradient-to-b from-cyan-500/5 to-transparent pointer-events-none blur-3xl"></div>
            
            <div className="flex flex-wrap justify-between items-center mb-8 gap-4 z-10">
              <div>
                <h2 className="text-xl font-bold tracking-wide">
                  {selectedPair.slice(0,3)}/{selectedPair.slice(3,6)} <span className="text-zinc-500 font-normal ml-2">Chart</span>
                </h2>
                <p className="text-sm text-cyan-400 mt-1">SMA (20) & Bollinger Bands</p>
              </div>
              <div className="flex gap-2 bg-black/40 p-1 rounded-xl border border-white/5">
                {['1w', '1m', '3m', '6m', '1y'].map(tf => (
                  <button 
                    key={tf} 
                    onClick={() => setSelectedPeriod(tf)}
                    className={`px-4 py-1.5 rounded-lg text-xs font-semibold uppercase transition-all ${selectedPeriod === tf ? 'bg-zinc-800 text-white shadow-sm border border-white/10' : 'text-zinc-400 hover:text-zinc-200 border border-transparent'}`}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="flex-1 w-full relative z-10 min-h-[350px]">
              {loading && !data && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-sm z-20 rounded-2xl">
                  <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin"></div>
                </div>
              )}
              
              {data && data.chart_data && (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.chart_data} margin={{ top: 10, right: 0, bottom: 0, left: -20 }}>
                    <defs>
                      <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                    <XAxis 
                      dataKey="Date" 
                      stroke="#52525b" 
                      tick={{ fill: '#71717a', fontSize: 11 }}
                      tickFormatter={(val) => val ? val.substring(5, 10) : ''} 
                      minTickGap={40}
                      axisLine={false}
                      tickLine={false}
                      dy={10}
                    />
                    <YAxis 
                      domain={['auto', 'auto']} 
                      stroke="#52525b" 
                      tick={{ fill: '#71717a', fontSize: 11, fontFamily: 'monospace' }} 
                      tickFormatter={(val) => val.toFixed(4)}
                      axisLine={false}
                      tickLine={false}
                      dx={-10}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(9, 9, 11, 0.9)', 
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(63, 63, 70, 0.5)', 
                        borderRadius: '12px',
                        boxShadow: '0 10px 30px -10px rgba(0,0,0,0.5)'
                      }}
                      itemStyle={{ color: '#e4e4e7', fontWeight: 500 }}
                      labelStyle={{ color: '#a1a1aa', marginBottom: '8px', fontSize: '12px' }}
                    />
                    
                    <Line type="monotone" dataKey="bb_upper" stroke="rgba(168,85,247,0.4)" strokeWidth={1} strokeDasharray="3 3" dot={false} name="BB Upper" />
                    <Line type="monotone" dataKey="bb_lower" stroke="rgba(168,85,247,0.4)" strokeWidth={1} strokeDasharray="3 3" dot={false} name="BB Lower" />
                    <Line type="monotone" dataKey="sma_20" stroke="#a855f7" strokeWidth={1.5} dot={false} name="SMA (20)" />
                    <Area type="monotone" dataKey="Close" stroke="#06b6d4" strokeWidth={3} fillOpacity={1} fill="url(#colorClose)" name="Close Price" />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
          
        </main>
      </div>
    </div>
  );
}
