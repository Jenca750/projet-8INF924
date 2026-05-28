import { useState, useEffect } from 'react'
import axios from 'axios'
import { Key, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export default function Profile({ token, me }) {
  const [newPassword, setNewPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const showMessage = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage({ type: '', text: '' }), 5000)
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    if (!me) return
    setLoading(true)
    try {
      await axios.put(`${API_URL}/users/${me.id}/password`, { password: newPassword }, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      showMessage('success', 'Mot de passe mis à jour avec succès (backend + ntfy)')
      setNewPassword('')
    } catch (err) {
      showMessage('error', "Erreur lors de la mise à jour du mot de passe")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-white mb-2">Mon Profil</h1>
        <p className="text-slate-400">Gérez vos informations personnelles</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-xl flex items-center gap-3 border ${
          message.type === 'success' 
            ? 'bg-green-500/10 border-green-500/30 text-green-400' 
            : 'bg-red-500/10 border-red-500/30 text-red-400'
        }`}>
          {message.type === 'success' ? <CheckCircle2 size={20} /> : <AlertCircle size={20} />}
          {message.text}
        </div>
      )}

      <div className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl border border-slate-700/50 shadow-xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-purple-500/20 text-purple-400 rounded-lg">
            <Key size={24} />
          </div>
          <h2 className="text-xl font-semibold text-white">Changer mon mot de passe ({me?.username})</h2>
        </div>
        
        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Nouveau mot de passe</label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !newPassword}
            className="w-full flex justify-center items-center gap-2 py-3 px-4 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-xl font-medium transition-colors"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : 'Mettre à jour'}
          </button>
        </form>
      </div>
    </div>
  )
}
