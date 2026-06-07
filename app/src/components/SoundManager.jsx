import { useState } from 'react'
import axios from 'axios'
import { Upload, Play, Loader2, Music } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || '/api'

export default function SoundManager({ token, showMessage }) {
  const [loading, setLoading] = useState(false)
  const [previewUrl, setPreviewUrl] = useState('')
  const [audioFile, setAudioFile] = useState(null)

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setAudioFile(file)
      setPreviewUrl(URL.createObjectURL(file))
    }
  }

  const uploadToBackend = async () => {
    if (!audioFile) return
    setLoading(true)
    const formData = new FormData()
    formData.append('file', audioFile)

    try {
      await axios.post(`${API_URL}/sound`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      })
      showMessage('success', "Sonnette personnalisée mise à jour avec succès")
    } catch (err) {
      showMessage('error', err.response?.data?.detail || "Erreur lors de l'envoi")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl border border-slate-700/50 shadow-xl h-fit">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-pink-500/20 text-pink-400 rounded-lg">
          <Music size={24} />
        </div>
        <h2 className="text-xl font-semibold text-white">Sonnerie Personnalisée</h2>
      </div>

      <div className="space-y-6">
        <div className="p-4 bg-slate-900/50 border border-slate-700/50 rounded-xl space-y-4">
          <p className="text-sm text-slate-300">Choisissez un fichier MP3 :</p>
          <label className="flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors border border-slate-600 text-sm cursor-pointer w-full text-center">
            <Upload size={18} />
            <span>Sélectionner un fichier</span>
            <input 
              type="file" 
              accept=".mp3,audio/mpeg" 
              className="hidden" 
              onChange={handleFileUpload} 
            />
          </label>
        </div>

        {previewUrl && (
          <div className="p-4 bg-slate-900/50 border border-indigo-500/30 rounded-xl space-y-4">
            <div className="flex items-center gap-3 text-slate-200">
              <Play size={18} className="text-indigo-400" />
              <span className="text-sm font-medium">Aperçu du son :</span>
            </div>
            <audio src={previewUrl} controls className="w-full h-10 rounded-lg outline-none" />
            
            <button
              onClick={uploadToBackend}
              disabled={loading}
              className="w-full flex justify-center items-center gap-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-medium transition-colors"
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <><Upload size={18} /> Définir comme sonnette</>}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
