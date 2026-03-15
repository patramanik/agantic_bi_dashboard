import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Zap, UserPlus, Loader2, ArrowLeft, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Signup() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Neural protocols mismatch: Passwords do not align.');
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      await register({ 
        full_name: fullName, 
        email: email, 
        password: password 
      });
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Email might already be registered.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-950 px-4 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-600/10 blur-[120px] -z-10 rounded-full" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-indigo-600/5 blur-[100px] -z-10 rounded-full" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel w-full max-w-md p-10 border border-white/10"
      >
        <div className="flex flex-col items-center mb-8 text-center">
          <div className="p-3 bg-emerald-600 rounded-2xl shadow-xl shadow-emerald-600/20 mb-6">
            <Zap className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Create Account</h1>
          <p className="text-slate-400 mt-2 text-sm font-medium italic">Initialize Neural Identity</p>
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

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Full Name</label>
            <input
              type="text"
              className="w-full bg-white/5 border border-white/5 rounded-xl px-5 py-3.5 text-white focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-slate-600 text-sm"
              placeholder="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Email</label>
            <input
              type="email"
              className="w-full bg-white/5 border border-white/5 rounded-xl px-5 py-3.5 text-white focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-slate-600 text-sm"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Password</label>
              <input
                type="password"
                className="w-full bg-white/5 border border-white/5 rounded-xl px-5 py-3.5 text-white focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-slate-600 text-sm"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Verify-Password</label>
              <input
                type="password"
                className="w-full bg-white/5 border border-white/5 rounded-xl px-5 py-3.5 text-white focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-slate-600 text-sm"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-900/40 disabled:opacity-50 mt-4"
          >
            {loading ? <Loader2 className="animate-spin" size={20} /> : <><ShieldCheck size={20} /> Create Account</>}
          </button>
        </form>

        <div className="mt-8 text-center border-t border-white/5 pt-8">
          <p className="text-slate-500 text-xs font-medium">
            Already have an account?{' '}
            <Link to="/login" className="text-emerald-400 hover:text-emerald-300 font-bold ml-1 inline-flex items-center gap-1 group">
              <ArrowLeft size={12} className="group-hover:-translate-x-1 transition-transform" /> Sign In
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
