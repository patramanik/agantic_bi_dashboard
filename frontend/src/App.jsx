import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { 
  Upload, PieChart as PieIcon, BarChart2, 
  TrendingUp, DollarSign, Users, Activity, LayoutGrid, Zap,
  LogOut, User as UserIcon, Database, History, Trash2, X, Loader2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import MetricCard from './components/ui/MetricCard';
import DynamicChart from './components/ui/DynamicChart';
import FloatingChat from './components/chat/FloatingChat';
import Login from './components/auth/Login';
import Signup from './components/auth/Signup';
import { useAuth } from './context/AuthContext';
import { 
  uploadFile, queryData, 
  getDatasets, deleteDataset, getHistory 
} from './utils/api';

// --- Dashboard Component ---
function Dashboard() {
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Neural Analytics System Online. Identity verified. Connect your data source to begin synthesis.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [fileId, setFileId] = useState(null);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const [visualizations, setVisualizations] = useState([]);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [datasets, setDatasets] = useState([]);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
        fetchInitialData();
    }
  }, [user]);

  const fetchInitialData = async () => {
    try {
      const ds = await getDatasets();
      setDatasets(ds.data);
    } catch (err) {
      console.error("Failed to fetch datasets");
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleDeleteDataset = async (filename) => {
    try {
      await deleteDataset(filename);
      setDatasets(prev => prev.filter(d => d.filename !== filename));
      if (fileId === filename) {
        setFileId(null);
        setMetrics([]);
        setVisualizations([]);
        setCurrentAnalysis(null);
      }
    } catch (err) {
      console.error("Deletion failed");
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);

    try {
      const response = await uploadFile(formData);
      setFileId(response.data.filename);
      const ds = await getDatasets();
      setDatasets(ds.data);
      
      const queryResponse = await queryData("dashboard summary", response.data.filename);
      if (queryResponse.data.viz === 'dashboard') {
        setMetrics(queryResponse.data.data.metrics);
        setVisualizations(queryResponse.data.data.visualizations);
      }

      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: `Synthesis complete for ${file.name}. Adaptive dashboard projections initialized.` 
      }]);
      setIsChatOpen(true);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Connection failure during data ingestion.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (msg) => {
    if (!msg.trim() || !fileId || loading) return;
    setMessages(prev => [...prev, { role: 'user', content: msg }]);
    if (msg === input) setInput('');
    setLoading(true);

    try {
      const response = await queryData(msg, fileId);
      
      if (response.data.viz === 'dashboard') {
        setMetrics(response.data.data.metrics);
        setVisualizations(response.data.data.visualizations);
        setCurrentAnalysis(null);
      } else if (response.data.viz !== 'table') {
        // For specific charts requested via chat, we want to show them prominently 
        // but maybe also allow pinning them to the dashboard.
        // For now, let's show as current analysis AND add to a "Recent Insights" list if unique
        setCurrentAnalysis(response.data);
        
        // Optionally append to visualizations if not already there
        setVisualizations(prev => {
            const exists = prev.some(v => v.title === response.data.answer);
            if (!exists) {
                return [{
                    title: response.data.answer,
                    viz: response.data.viz,
                    data: response.data.data,
                    isChatGenerated: true
                }, ...prev];
            }
            return prev;
        });
      } else {
        setCurrentAnalysis(response.data);
      }

      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: response.data.answer,
        viz: response.data.viz,
        data: response.data.data
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Logic error encountered in synthesis.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden flex flex-col bg-slate-950">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-600/10 blur-[120px] -z-10 rounded-full" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-emerald-600/5 blur-[100px] -z-10 rounded-full" />

      {/* Header */}
      <header className="px-8 py-4 flex justify-between items-center border-b border-white/5 bg-slate-950/40 backdrop-blur-xl sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-600/20">
            <Zap className="text-white" size={20} />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              Conversational BI
              <span className="text-[9px] font-mono bg-indigo-500/20 text-indigo-400 px-1.5 py-0.5 rounded border border-indigo-500/20 uppercase tracking-tighter">Secure v2.5</span>
            </h1>
          </div>
        </div>
        
        <div className="flex items-center gap-5">
          <div className="hidden md:flex items-center gap-4 border-r border-white/10 pr-5 mr-1">
            <button 
                onClick={() => setIsHistoryOpen(true)}
                className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-white transition-colors"
            >
                <Database size={14} className="text-indigo-400" /> Matrix Assets
            </button>
            <div className="flex items-center gap-2 text-xs font-bold text-slate-400">
               <div className={`w-1.5 h-1.5 rounded-full ${fileId ? 'bg-emerald-500 animate-pulse' : 'bg-slate-700'}`} />
               {fileId ? fileId : 'Neural Idle'}
            </div>
          </div>

          <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".csv,.xlsx" />
          <button 
            onClick={() => fileInputRef.current.click()} 
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-indigo-900/40 disabled:opacity-50"
          >
            <Upload size={14} /> {fileId ? 'Change Source' : 'Connect Data'}
          </button>

          <div className="flex items-center gap-3 ml-2 group relative">
            <div className="flex flex-col items-end mr-1">
              <span className="text-[11px] font-bold text-white uppercase tracking-tight">{user?.full_name || user?.username}</span>
              <span className="text-[9px] text-slate-500 font-medium">Neural Operative</span>
            </div>
            <button onClick={handleLogout} className="p-2.5 bg-white/5 hover:bg-red-500/20 text-slate-400 hover:text-red-400 rounded-xl transition-all border border-white/5">
                <LogOut size={16} />
            </button>
          </div>
        </div>
      </header>

      {/* History/Dataset Sidebar */}
      <AnimatePresence>
        {isHistoryOpen && (
            <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex justify-end"
                onClick={() => setIsHistoryOpen(false)}
            >
                <motion.div 
                    initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
                    className="w-full max-w-sm bg-slate-900 border-l border-white/10 h-full flex flex-col"
                    onClick={e => e.stopPropagation()}
                >
                    <div className="p-6 border-b border-white/5 flex justify-between items-center">
                        <h2 className="text-white font-bold flex items-center gap-2 italic">
                            <Database size={18} className="text-indigo-500" /> Encrypted Assets
                        </h2>
                        <button onClick={() => setIsHistoryOpen(false)} className="text-slate-500 hover:text-white"><X size={20} /></button>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {datasets.length > 0 ? datasets.map((d, i) => (
                            <div key={i} className="p-4 bg-white/5 rounded-2xl border border-white/5 group hover:border-indigo-500/30 transition-all">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-xs font-bold text-white truncate max-w-[200px]">{d.filename}</span>
                                    <button 
                                        onClick={() => handleDeleteDataset(d.filename)}
                                        className="text-slate-600 hover:text-red-400 p-1 opacity-10 group-hover:opacity-100 transition-opacity"
                                    >
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                                <div className="flex gap-4 text-[10px] text-slate-500 font-mono">
                                    <span>{d.rows_count} Rows</span>
                                    <span>{new Date(d.created_at).toLocaleDateString()}</span>
                                </div>
                                <button 
                                    onClick={() => { setFileId(d.filename); setIsHistoryOpen(false); handleAction("dashboard summary"); }}
                                    className="mt-3 w-full py-1.5 text-[10px] font-bold uppercase tracking-widest text-indigo-400 hover:text-indigo-300 border border-indigo-500/20 hover:bg-indigo-500/10 rounded-lg transition-all"
                                >
                                    Activate Signal
                                </button>
                            </div>
                        )) : (
                            <div className="h-full flex flex-col items-center justify-center opacity-20 text-slate-500">
                                <History size={48} className="mb-4" />
                                <p>No matrix records found.</p>
                            </div>
                        )}
                    </div>
                </motion.div>
            </motion.div>
        )}
      </AnimatePresence>

      <main className="flex-1 overflow-y-auto p-8 max-w-[1600px] mx-auto w-full">
        <section className="flex gap-6 mb-10 flex-wrap">
          {metrics.length > 0 ? metrics.map((m, i) => (
              <MetricCard 
                key={i} label={m.label} value={m.value}
                icon={[DollarSign, TrendingUp, Users][i % 3]} 
                color={['#818cf8', '#34d399', '#fbbf24'][i % 3]} 
              />
          )) : (
            <div className="glass-panel flex-1 p-12 text-center flex flex-col items-center justify-center border-dashed border-slate-700/50">
              <Activity className="text-slate-700 mb-4" size={48} />
              <p className="text-slate-500 font-medium italic">Neural metrics offline. Identity verified. Awaiting source connection.</p>
            </div>
          )}
        </section>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 mb-20 px-1">
          {visualizations.length > 0 ? visualizations.map((v, i) => (
              <motion.div 
                initial={{ opacity: 0, y: 20 }} 
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                key={i} 
                className={`glass-panel h-[450px] p-6 flex flex-col group relative ${v.isChatGenerated ? 'border-indigo-500/40 shadow-lg shadow-indigo-500/5' : ''}`}
              >
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2 italic truncate pr-4">
                    {v.viz === 'pie' ? <PieIcon size={12} className="text-emerald-500" /> : 
                     v.viz === 'area' ? <TrendingUp size={12} className="text-indigo-500" /> :
                     <LayoutGrid size={12} className="text-indigo-500" />}
                    {v.title}
                  </h3>
                  {v.isChatGenerated && (
                    <span className="text-[8px] font-mono bg-indigo-500/20 text-indigo-400 px-1.5 py-0.5 rounded border border-indigo-500/20 uppercase">Pin</span>
                  )}
                </div>
                <div className="flex-1 bg-black/20 rounded-2xl overflow-hidden border border-white/5 flex items-center justify-center p-2">
                  <DynamicChart data={v.data} type={v.viz} title={v.title} />
                </div>
              </motion.div>
          )) : currentAnalysis ? (
            <div className="glass-panel col-span-full h-[550px] p-8 flex flex-col">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <Activity size={16} className="text-indigo-500" />
                  Signal Analysis: {currentAnalysis.viz}
                </h3>
              </div>
              <div className="flex-1 bg-black/20 rounded-2xl overflow-hidden border border-white/5 flex items-center justify-center p-4">
                 <DynamicChart data={currentAnalysis.data} type={currentAnalysis.viz} title={currentAnalysis.answer} />
              </div>
            </div>
          ) : (
            <div className="glass-panel col-span-full h-[400px] flex flex-col items-center justify-center text-slate-600 font-bold italic opacity-30 border-dashed border-slate-800">
               <Zap size={64} className="mb-4 animate-pulse" />
               <div className="text-center">
                 <p className="tracking-[0.5em] mb-2">NEURAL CORE READY</p>
                 <p className="text-[10px] opacity-50 not-italic">Connect data source to initialize synthesis</p>
               </div>
            </div>
          )}
        </div>
      </main>

      <FloatingChat 
        isChatOpen={isChatOpen} setIsChatOpen={setIsChatOpen}
        messages={messages} loading={loading} handleAction={handleAction}
        fileId={fileId} input={input} setInput={setInput}
      />
    </div>
  );
}

export default function App() {
  const { token, loading } = useAuth();

  if (loading) {
    return (
        <div className="min-h-screen w-full flex flex-col items-center justify-center bg-slate-950 gap-4">
            <Loader2 className="animate-spin text-indigo-500" size={48} />
            <p className="text-slate-500 font-mono text-sm animate-pulse tracking-widest">INITIALIZING NEURAL AUTH...</p>
        </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route 
          path="/" 
          element={token ? <Dashboard /> : <Navigate to="/login" />} 
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}
