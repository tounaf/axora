'use client'

import React from 'react'
import { Sparkles, Layers, ChevronDown } from 'lucide-react'

export const TopHeader: React.FC = () => {
  return (
    <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between flex-shrink-0">
      <div className="flex items-center space-x-3">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200/70 shadow-xs">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          Mode Agent
        </span>
        <button className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 shadow-xs transition" type="button">
          <Layers className="w-3.5 h-3.5 text-slate-500" />
          <span>Domaine : <strong className="font-semibold text-slate-900">Gestion paroissiale (v0.2)</strong></span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-0.5" />
        </button>
      </div>
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 pl-2 cursor-pointer group">
          <div className="w-7 h-7 rounded-full bg-[#0b3b82] text-white flex items-center justify-center text-xs font-bold ring-2 ring-blue-100">
            JD
          </div>
          <span className="text-xs font-medium text-slate-700 group-hover:text-slate-900">Jean Dupont</span>
        </div>
      </div>
    </header>
  )
}
