import { useState, useEffect } from 'react'
import axios from 'axios'
import { Users as UsersIcon, Plus, Loader2, CheckCircle2, AlertCircle, Trash2, User } from 'lucide-react'
import SoundManager from './SoundManager'

const API_URL = import.meta.env.VITE_API_URL || '/api'

export default function Admin({ token, me }) {
  const [users, setUsers] = useState([])
  const [newUser, setNewUser] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_URL}/users`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUsers(response.data)
    } catch (err) {
      console.error("Failed to fetch users", err)
    }
  }

  useEffect(() => {
    if (me?.is_admin) {
      fetchUsers()
    }
  }, [token, me])

  const showMessage = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage({ type: '', text: '' }), 5000)
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await axios.post(`${API_URL}/users`, newUser, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      showMessage('success', `Utilisateur ${newUser.username} créé avec succès`)
      setNewUser({ username: '', password: '' })
      fetchUsers()
    } catch (err) {
      showMessage('error', err.response?.data?.detail || "Erreur lors de la création")
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteUser = async (userId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cet utilisateur ?")) return
    
    try {
      await axios.delete(`${API_URL}/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      showMessage('success', 'Utilisateur supprimé avec succès')
      fetchUsers()
    } catch (err) {
      showMessage('error', err.response?.data?.detail || "Erreur lors de la suppression")
    }
  }

  if (!me?.is_admin) {
    return (
      <div className="p-8 max-w-5xl mx-auto">
        <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-xl flex items-center justify-center text-red-400 gap-3">
          <AlertCircle size={24} />
          <span>Accès refusé. Vous devez être administrateur pour voir cette page.</span>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 md:p-8 max-w-5xl mx-auto space-y-8 pb-8">
      <div className="mb-4">
        <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">Espace Administration</h1>
        <p className="text-slate-400">Gérez les accès de la plateforme et les abonnements aux notifications</p>
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

      <div className="grid md:grid-cols-2 gap-8">
        {/* User List */}
        <div className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl border border-slate-700/50 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg">
              <User size={24} />
            </div>
            <h2 className="text-xl font-semibold text-white">Utilisateurs inscrits</h2>
          </div>
          <div className="space-y-3">
            {users.map(u => (
              <div key={u.id} className="flex items-center justify-between p-4 bg-slate-900/50 border border-slate-700/50 rounded-xl">
                <div className="flex items-center gap-3 text-slate-200">
                  <span className="font-medium">{u.username}</span>
                  {u.is_admin && <span className="text-xs bg-indigo-500/20 text-indigo-400 px-2 py-1 rounded-full">Admin</span>}
                </div>
                {u.id !== me.id && (
                  <button 
                    onClick={() => handleDeleteUser(u.id)}
                    className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>
            ))}
            {users.length === 0 && <p className="text-slate-400 text-center py-4">Aucun autre utilisateur.</p>}
          </div>
        </div>

        {/* Create User Card */}
        <div className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl border border-slate-700/50 shadow-xl h-fit">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg">
              <UsersIcon size={24} />
            </div>
            <h2 className="text-xl font-semibold text-white">Créer un utilisateur</h2>
          </div>
          
          <form onSubmit={handleCreateUser} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Nom d'utilisateur</label>
              <input
                type="text"
                required
                value={newUser.username}
                onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                className="w-full bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="Ex: famille"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Mot de passe</label>
              <input
                type="password"
                required
                value={newUser.password}
                onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                className="w-full bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !newUser.username || !newUser.password}
              className="w-full flex justify-center items-center gap-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-medium transition-colors"
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <><Plus size={18} /> Créer l'utilisateur</>}
            </button>
          </form>
        </div>

        {/* Sound Manager Card */}
        <SoundManager token={token} showMessage={showMessage} />
      </div>
    </div>
  )
}
