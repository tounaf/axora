'use client'

import React from 'react'
import { BarChart3, PieChart as PieIcon } from 'lucide-react'

interface SeriesItem {
  label: string
  value: number
  color?: string
}

interface ChartViewProps {
  title?: string
  description?: string
  data: {
    chart_type?: 'bar' | 'donut' | 'pie' | 'line'
    x_label?: string
    y_label?: string
    series: SeriesItem[]
  }
}

export const ChartView: React.FC<ChartViewProps> = ({ title, description, data }) => {
  const { chart_type = 'bar', series = [], x_label, y_label } = data

  const maxValue = Math.max(...series.map((s) => s.value), 1)

  return (
    <div className="border border-slate-200 rounded-xl p-4 bg-white shadow-xs space-y-4 mt-3">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
        <div className="flex items-center gap-2">
          {chart_type === 'bar' ? (
            <BarChart3 className="w-4 h-4 text-blue-600" />
          ) : (
            <PieIcon className="w-4 h-4 text-indigo-600" />
          )}
          <h4 className="text-xs font-bold text-slate-900">{title || 'Statistiques'}</h4>
        </div>
        {description && <span className="text-[11px] text-slate-500">{description}</span>}
      </div>

      {chart_type === 'bar' && (
        <div className="space-y-3 pt-1">
          {series.map((item, idx) => {
            const percentage = Math.round((item.value / maxValue) * 100)
            return (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-medium text-slate-700">
                  <span>{item.label}</span>
                  <span className="font-bold text-slate-900">{item.value}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden flex">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: item.color || '#1d4ed8',
                    }}
                  />
                </div>
              </div>
            )
          })}
          {x_label && <p className="text-[10px] text-slate-400 text-right italic pt-1">{x_label}</p>}
        </div>
      )}

      {(chart_type === 'donut' || chart_type === 'pie') && (
        <div className="flex flex-wrap items-center justify-around gap-4 py-2">
          <div className="relative w-28 h-28 flex items-center justify-center">
            {/* Simple Circular SVG Donut */}
            <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
              {series.map((item, idx) => {
                const total = series.reduce((sum, s) => sum + s.value, 0) || 1
                const pct = (item.value / total) * 100
                const strokeDasharray = `${pct} ${100 - pct}`
                return (
                  <circle
                    key={idx}
                    cx="18"
                    cy="18"
                    r="15.91549430918954"
                    fill="transparent"
                    stroke={item.color || '#1d4ed8'}
                    strokeWidth="3.5"
                    strokeDasharray={strokeDasharray}
                    strokeDashoffset="0"
                  />
                )
              })}
            </svg>
            <div className="absolute text-center">
              <span className="text-xs font-bold text-slate-800">
                {series.reduce((sum, s) => sum + s.value, 0)}
              </span>
              <p className="text-[9px] text-slate-400">Total</p>
            </div>
          </div>

          <div className="space-y-1.5">
            {series.map((item, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs text-slate-700">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color || '#1d4ed8' }} />
                <span>{item.label} :</span>
                <strong className="text-slate-900">{item.value}</strong>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
