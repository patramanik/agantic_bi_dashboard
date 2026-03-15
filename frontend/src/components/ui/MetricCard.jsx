import React from 'react';
import { TrendingUp } from 'lucide-react';

const MetricCard = ({ label, value, icon: Icon, color }) => (
  <div className="glass-panel p-6 flex-1 min-w-[240px] flex flex-col gap-3 group transition-all duration-300">
    <div className="flex justify-between items-center">
      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</span>
      <div className="p-2.5 rounded-xl bg-slate-800/50 border border-white/5 transition-colors group-hover:border-indigo-500/30">
        <Icon size={18} color={color} />
      </div>
    </div>
    <div className="text-3xl font-bold tracking-tight text-white font-outfit">
      {typeof value === 'number' ? value.toLocaleString(undefined, { maximumFractionDigits: 0 }) : value}
    </div>
    <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 font-medium bg-emerald-400/5 py-1 px-2 rounded-full w-fit">
      <TrendingUp size={10} /> <span>Live Insight</span>
    </div>
  </div>
);

export default MetricCard;
