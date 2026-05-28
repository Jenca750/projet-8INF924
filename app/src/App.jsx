import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom'
import axios from 'axios'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import Profile from './components/Profile'
import Admin from './components/Admin'
import { Bell, Activity, Users as UsersIcon, LogOut, User as UserIcon } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || '/api'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [me, setMe] = useState(null)

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
      axios.get(`${API_URL}/users/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then(res => setMe(res.data))
        .catch(() => setToken(null))
    } else {
      localStorage.removeItem('token')
      setMe(null)
    }
  }, [token])

  const handleLogout = () => {
    setToken(null)
  }

  if (!token) {
    return <Login setToken={setToken} />
  }

  return (
    <Router>
      <div className="flex h-screen bg-slate-900 text-white font-sans overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
          <div className="p-6 flex items-center gap-3">
            <div className="p-2 bg-indigo-500 rounded-lg">
              <Bell size={24} className="text-white" />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">IoT Doorbell</h1>
          </div>
          
          <nav className="flex-1 px-4 space-y-2 mt-4">
            <Link to="/" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-700/50 transition-colors text-slate-300 hover:text-white">
              <Activity size={20} />
              <span>Event Logs</span>
            </Link>
            <Link to="/profile" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-700/50 transition-colors text-slate-300 hover:text-white">
              <UserIcon size={20} />
              <span>Profile</span>
            </Link>
            {me?.is_admin && (
              <Link to="/admin" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-700/50 transition-colors text-slate-300 hover:text-white">
                <UsersIcon size={20} />
                <span>Admin</span>
              </Link>
            )}
          </nav>

          <div className="p-4 border-t border-slate-700">
            <div className="mb-2 px-4 text-sm text-slate-500 flex justify-between items-center">
              <span>{me?.username}</span>
              {me?.is_admin && <span className="text-xs bg-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded-full">Admin</span>}
            </div>
            <button 
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-3 w-full rounded-xl hover:bg-red-500/10 hover:text-red-400 transition-colors text-slate-400"
            >
              <LogOut size={20} />
              <span>Logout</span>
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto bg-slate-900 relative">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl -z-10 mix-blend-screen pointer-events-none"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl -z-10 mix-blend-screen pointer-events-none"></div>
          
          <Routes>
            <Route path="/" element={<Dashboard token={token} />} />
            <Route path="/profile" element={<Profile token={token} me={me} />} />
            <Route path="/admin" element={<Admin token={token} me={me} />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
