import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Zap, LogIn, Loader2, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError('Invalid credentials. Access Denied.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-950 px-4 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-600/10 blur-[120px] -z-10 rounded-full" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-emerald-600/5 blur-[100px] -z-10 rounded-full" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel w-full max-w-md p-10 border border-white/10"
      >
        <div className="flex flex-col items-center mb-10 text-center">
          <div className="p-3 bg-indigo-600 rounded-2xl shadow-xl shadow-indigo-600/20 mb-6">
            <Zap className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Sign In</h1>
          <p className="text-slate-400 mt-2 text-sm font-medium italic">Neural BI Synthesis Portal</p>
        </div>

        {error && (
            <motion.div 
                initial={{ scale: 0.95 }}
                animate={{ scale: 1 }}
                className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-xl text-center font-medium"
            >
                {error}
            </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Email</label>
            <input
              type="text"
              className="w-full bg-white/5 border border-white/5 rounded-xl px-5 py-4 text-white focus:outline-none focus:border-indigo-500/50 transition-all placeholder:text-slate-600"
              placeholder="Email address"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Password</label>
            <input
              type="password"
              className="w-full bg-white/5 border border-white/5 rounded-xl px-5 py-4 text-white focus:outline-none focus:border-indigo-500/50 transition-all placeholder:text-slate-600"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-900/40 disabled:opacity-50"
          >
            {loading ? <Loader2 className="animate-spin" size={20} /> : <><LogIn size={20} /> Sign In</>}
          </button>
        </form>

        <div className="mt-10 text-center">
          <p className="text-slate-500 text-xs font-medium">
            New user?{' '}
            <Link to="/signup" className="text-indigo-400 hover:text-indigo-300 font-bold ml-1 inline-flex items-center gap-1 group">
              Register <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform" />
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
