'use client'

import React from 'react'
import { Activity, CheckCircle, AlertTriangle, AlertCircle } from 'lucide-react'

interface MetricCard {
  label: string
  value: string | number
  description?: string
  status?: 'neutral' | 'success' | 'warning' | 'danger'
}

interface MetricCardViewProps {
  title?: string
  description?: string
  data: {
    cards: MetricCard[]
  }
}

export const MetricCardView: React.FC<MetricCardViewProps> = ({ title, description, data }) => {
  const { cards = [] } = data

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-amber-500" />
      case 'danger':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Activity className="w-4 h-4 text-blue-500" />
    }
  }

  return (
    <div className="border border-slate-200 rounded-xl p-4 bg-white shadow-xs space-y-3 mt-3">
      {title && (
        <div className="border-b border-slate-100 pb-2 flex items-center justify-between">
          <h4 className="text-xs font-bold text-slate-900">{title}</h4>
          {description && <span className="text-[11px] text-slate-500">{description}</span>}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {cards.map((card, idx) => (
          <div key={idx} className="bg-slate-50/70 border border-slate-200/80 rounded-xl p-3.5 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-slate-500">{card.label}</span>
              {getStatusBadge(card.status)}
            </div>
            <div className="text-xl font-bold text-slate-900">{card.value}</div>
            {card.description && <p className="text-[10px] text-slate-400">{card.description}</p>}
          </div>
        ))}
      </div>
    </div>
  )
}
