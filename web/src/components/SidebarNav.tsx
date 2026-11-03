'use client'

import React from 'react'
import { MessageSquare, Network, Database, Wrench } from 'lucide-react'

interface SidebarNavProps {
  onQuickAction?: (text: string) => void
}

export const SidebarNav: React.FC<SidebarNavProps> = ({ onQuickAction }) => {
  return (
    <aside className="w-64 bg-[#081528] text-slate-300 flex flex-col justify-between flex-shrink-0 z-20">
      <div className="flex flex-col">
        <div className="px-6 pt-6 pb-8 flex items-center space-x-3.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-sky-400 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L2 19.5h5l2-4h6l2 4h5L12 2zm-1.8 11.2L12 7.8l1.8 5.4h-3.6z"></path>
            </svg>
          </div>
          <div>
            <div className="text-xl font-bold tracking-tight text-white flex items-center gap-1">Axora</div>
            <p className="text-[11px] text-slate-400 font-medium tracking-wide">From intent to action.</p>
          </div>
        </div>
        <nav className="px-3 space-y-1">
          <a className="flex items-center space-x-3 px-3.5 py-2.5 rounded-lg bg-[#1a56db] text-white font-medium text-sm transition shadow-sm" href="#">
            <MessageSquare className="w-5 h-5 opacity-90" />
            <span>Assistant</span>
          </a>
          <button
            type="button"
            onClick={() => alert('Modèle sémantique: gestion_paroissiale (v0.2)\nEntités: Paroisse, ZoneGeographique, Membre, Association')}
            className="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-[#13233c] text-sm font-medium transition text-left"
          >
            <Network className="w-5 h-5 opacity-75" />
            <span>Modèle métier</span>
          </button>
          <button
            type="button"
            onClick={() => onQuickAction && onQuickAction('Lister tous les membres')}
            className="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-[#13233c] text-sm font-medium transition text-left"
          >
            <Database className="w-5 h-5 opacity-75" />
            <span>Données</span>
          </button>
          <button
            type="button"
            onClick={() => alert('Outils enregistrés:\n- discover_model\n- query_data\n- create_record\n- update_record')}
            className="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-[#13233c] text-sm font-medium transition text-left"
          >
            <Wrench className="w-5 h-5 opacity-75" />
            <span>Outils</span>
          </button>
        </nav>
      </div>
      <div className="p-4 border-t border-slate-800/80">
        <div className="bg-[#0f1f38] border border-slate-800 rounded-xl p-3">
          <div className="flex items-center space-x-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-semibold text-slate-200">Système opérationnel</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 pl-4.5">API • Base de données • LLM</p>
        </div>
        <div className="mt-3 px-1 text-[11px] text-slate-500 font-mono">v0.5.0</div>
      </div>
    </aside>
  )
}
