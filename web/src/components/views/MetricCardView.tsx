'use client'

import React from 'react'
import { Activity, CheckCircle, AlertTriangle, AlertCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface MetricCard {
  label: string
  value: string | number
  description?: string
  trend?: string
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

  const getTrendIcon = (trend?: string) => {
    if (!trend) return null
    if (trend.startsWith('+') || trend.toLowerCase().includes('hausse')) {
      return <TrendingUp className="w-3.5 h-3.5 text-emerald-600 inline mr-1" />
    }
    if (trend.startsWith('-') || trend.toLowerCase().includes('baisse')) {
      return <TrendingDown className="w-3.5 h-3.5 text-red-600 inline mr-1" />
    }
    return <Minus className="w-3.5 h-3.5 text-slate-400 inline mr-1" />
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
          <div key={idx} className="bg-slate-50/70 border border-slate-200/80 rounded-xl p-4 space-y-2 hover:border-slate-300 transition">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">{card.label}</span>
              {getStatusBadge(card.status)}
            </div>
            <div className="text-2xl font-extrabold text-slate-900 tracking-tight">{card.value}</div>
            <div className="flex items-center justify-between text-[11px] pt-1">
              {card.trend && (
                <div className="flex items-center font-semibold text-slate-700">
                  {getTrendIcon(card.trend)}
                  <span>{card.trend}</span>
                </div>
              )}
              {card.description && (
                <p className="text-[11px] text-slate-400">{card.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
