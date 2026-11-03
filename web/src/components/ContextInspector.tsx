'use client'

import React from 'react'
import { Lightbulb, Network, Database } from 'lucide-react'

interface ContextInspectorProps {
  summary?: string
}

export const ContextInspector: React.FC<ContextInspectorProps> = ({ summary = "Prêt à analyser vos intentions métier." }) => {
  return (
    <aside className="w-80 bg-white border-l border-slate-200 flex flex-col flex-shrink-0 overflow-y-auto">
      <div className="flex border-b border-slate-200 px-4 pt-3 gap-6 text-xs font-semibold">
        <button className="pb-3 text-blue-600 border-b-2 border-blue-600 transition" type="button">Contexte</button>
        <button className="pb-3 text-slate-500 hover:text-slate-700 transition" type="button" onClick={() => alert('Outils enregistrés:\n- discover_model\n- query_data\n- create_record\n- update_record')}>Outils</button>
      </div>
      <div className="p-5 space-y-4 text-xs">
        <div className="border border-slate-200 rounded-xl p-4 bg-white shadow-2xs space-y-2">
          <div className="flex items-center space-x-2 text-slate-800 font-semibold">
            <Lightbulb className="w-4 h-4 text-amber-500" />
            <span>Résumé de la requête</span>
          </div>
          <p className="text-slate-600 text-[11px] leading-relaxed">
            {summary}
          </p>
        </div>
        <div className="border border-slate-200 rounded-xl p-4 bg-white shadow-2xs space-y-3">
          <div className="flex items-center space-x-2 text-slate-800 font-semibold">
            <Network className="w-4 h-4 text-blue-600" />
            <span>Concepts mobilisés</span>
          </div>
          <div className="space-y-2.5">
            <div>
              <div className="flex items-center gap-1.5 font-medium text-slate-900">
                <span>Membre</span>
                <span className="px-1.5 py-0.5 text-[9px] bg-emerald-50 text-emerald-600 border border-emerald-200 rounded">canonique</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">Synonymes : adhérent, fidèle</div>
            </div>
            <div>
              <div className="flex items-center gap-1.5 font-medium text-slate-900">
                <span>Paroisse</span>
                <span className="px-1.5 py-0.5 text-[9px] bg-emerald-50 text-emerald-600 border border-emerald-200 rounded">canonique</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">Synonymes : église, communauté</div>
            </div>
          </div>
        </div>
        <div className="border border-slate-200 rounded-xl p-4 bg-white shadow-2xs space-y-3">
          <div className="flex items-center space-x-2 text-slate-800 font-semibold">
            <Database className="w-4 h-4 text-indigo-600" />
            <span>Données consultées</span>
          </div>
          <div>
            <span className="text-[11px] text-slate-500 font-medium">Table(s) :</span>
            <div className="flex flex-wrap gap-1.5 mt-1">
              <span className="px-2 py-0.5 bg-slate-100 text-slate-700 text-[11px] rounded font-mono">membre</span>
              <span className="px-2 py-0.5 bg-slate-100 text-slate-700 text-[11px] rounded font-mono">paroisse</span>
              <span className="px-2 py-0.5 bg-slate-100 text-slate-700 text-[11px] rounded font-mono">association</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
