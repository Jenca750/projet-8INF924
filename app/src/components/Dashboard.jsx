import { useState, useEffect } from 'react'
import axios from 'axios'
import { Activity, Bell, MapPin, Clock, Loader2, RefreshCw } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export default function Dashboard({ token }) {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_URL}/logs`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setLogs(response.data)
    } catch (err) {
      console.error("Failed to fetch logs", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
    // Optional: Set up an interval to fetch logs automatically
    // const interval = setInterval(fetchLogs, 10000)
    // return () => clearInterval(interval)
  }, [token])

  const formatDate = (dateString) => {
    const d = new Date(dateString)
    return d.toLocaleString('fr-FR', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    })
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Event Logs</h1>
          <p className="text-slate-400">Derniers événements de la sonnette connectée</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={async () => {
              const espToken = window.prompt("Veuillez entrer le token ESP32 :");
              if (!espToken) return;
              try {
                await axios.post(`${API_URL}/events`, { event_type: 'button', details: 'Simulation manuelle' }, {
                  headers: { Authorization: `Bearer ${espToken}` }
                });
                fetchLogs();
                alert("Évènement simulé avec succès !");
              } catch (err) {
                alert("Erreur lors de la simulation : " + (err.response?.data?.detail || err.message));
              }
            }}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-xl text-white transition-colors border border-indigo-500"
          >
            <Bell size={18} />
            Simuler un évènement
          </button>
          <button 
            onClick={fetchLogs}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-slate-300 transition-colors border border-slate-700"
          >
            <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
            Actualiser
          </button>
        </div>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl border border-slate-700/50 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-700/50 text-slate-400 text-sm bg-slate-800/80">
                <th className="p-4 font-medium pl-6">Type d'Événement</th>
                <th className="p-4 font-medium">Date & Heure</th>
                <th className="p-4 font-medium">Détails</th>
              </tr>
            </thead>
            <tbody>
              {loading && logs.length === 0 ? (
                <tr>
                  <td colSpan="3" className="p-8 text-center text-slate-400">
                    <Loader2 className="animate-spin inline mr-2" /> Chargement...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan="3" className="p-8 text-center text-slate-500 italic">
                    Aucun événement enregistré.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="p-4 pl-6">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${log.event_type === 'button' ? 'bg-purple-500/20 text-purple-400' : 'bg-indigo-500/20 text-indigo-400'}`}>
                          {log.event_type === 'button' ? <Bell size={18} /> : <Activity size={18} />}
                        </div>
                        <span className="capitalize font-medium text-slate-200">
                          {log.event_type === 'button' ? 'Sonnerie' : 'Mouvement'}
                        </span>
                      </div>
                    </td>
                    <td className="p-4 text-slate-300">
                      <div className="flex items-center gap-2">
                        <Clock size={16} className="text-slate-500" />
                        {formatDate(log.timestamp)}
                      </div>
                    </td>
                    <td className="p-4 text-slate-400">
                      {log.details || <span className="italic opacity-50">Aucun</span>}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
