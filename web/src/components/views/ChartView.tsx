'use client'

import React from 'react'
import { BarChart3, PieChart as PieIcon, LineChart as LineIcon } from 'lucide-react'

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
    total?: number
  }
}

export const ChartView: React.FC<ChartViewProps> = ({ title, description, data }) => {
  const { chart_type = 'bar', series = [], x_label, y_label, total } = data

  const maxValue = Math.max(...series.map((s) => s.value), 1)
  const totalSum = total != null ? total : series.reduce((sum, s) => sum + s.value, 0) || 1

  // Helper for Pie/Camembert SVG sector calculation
  const getCoordinatesForPercent = (percent: number) => {
    const x = Math.cos(2 * Math.PI * percent)
    const y = Math.sin(2 * Math.PI * percent)
    return [x, y]
  }

  let cumulativePercent = 0

  return (
    <div className="border border-slate-200 rounded-xl p-4 bg-white shadow-xs space-y-4 mt-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
        <div className="flex items-center gap-2">
          {chart_type === 'bar' && <BarChart3 className="w-4 h-4 text-blue-600" />}
          {(chart_type === 'pie' || chart_type === 'donut') && <PieIcon className="w-4 h-4 text-indigo-600" />}
          {chart_type === 'line' && <LineIcon className="w-4 h-4 text-emerald-600" />}
          <h4 className="text-xs font-bold text-slate-900">{title || 'Visualisation Graphique'}</h4>
        </div>
        {description && <span className="text-[11px] text-slate-500">{description}</span>}
      </div>

      {/* 1. GRAPHIQUE EN BARRES */}
      {chart_type === 'bar' && (
        <div className="space-y-3 pt-1">
          {series.map((item, idx) => {
            const percentage = Math.round((item.value / maxValue) * 100)
            return (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-medium text-slate-700">
                  <span>{item.label}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900">{item.value}</span>
                    <span className="text-[10px] text-slate-400">({Math.round((item.value / totalSum) * 100)}%)</span>
                  </div>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden flex shadow-inner">
                  <div
                    className="h-full rounded-full transition-all duration-500 shadow-sm"
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

      {/* 2. CAMEMBERT / PIE & DONUT */}
      {(chart_type === 'pie' || chart_type === 'donut') && (
        <div className="flex flex-wrap items-center justify-around gap-6 py-2">
          <div className="relative w-36 h-36 flex items-center justify-center">
            <svg viewBox="-1 -1 2 2" className="w-full h-full transform -rotate-90">
              {series.map((slice, idx) => {
                const slicePercent = slice.value / totalSum
                const startPercent = cumulativePercent
                cumulativePercent += slicePercent

                const [startX, startY] = getCoordinatesForPercent(startPercent)
                const [endX, endY] = getCoordinatesForPercent(cumulativePercent)
                const largeArcFlag = slicePercent > 0.5 ? 1 : 0

                // Full circle case
                if (slicePercent >= 0.999) {
                  return (
                    <circle
                      key={idx}
                      cx="0"
                      cy="0"
                      r="1"
                      fill={slice.color || '#1d4ed8'}
                    />
                  )
                }

                const pathData = `M 0 0 L ${startX} ${startY} A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY} Z`

                return (
                  <path
                    key={idx}
                    d={pathData}
                    fill={slice.color || '#1d4ed8'}
                    stroke="#ffffff"
                    strokeWidth="0.04"
                    className="hover:opacity-90 transition-opacity cursor-pointer"
                  />
                )
              })}
              {chart_type === 'donut' && (
                <circle cx="0" cy="0" r="0.6" fill="#ffffff" />
              )}
            </svg>
            {chart_type === 'donut' && (
              <div className="absolute text-center pointer-events-none">
                <span className="text-sm font-bold text-slate-800">{totalSum}</span>
                <p className="text-[9px] text-slate-400 uppercase tracking-wider">Total</p>
              </div>
            )}
          </div>

          <div className="space-y-2">
            {series.map((item, idx) => {
              const pct = Math.round((item.value / totalSum) * 100)
              return (
                <div key={idx} className="flex items-center justify-between gap-4 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-md flex-shrink-0" style={{ backgroundColor: item.color || '#1d4ed8' }} />
                    <span className="text-slate-700 font-medium">{item.label}</span>
                  </div>
                  <div className="flex items-center gap-1.5 font-mono">
                    <strong className="text-slate-900">{item.value}</strong>
                    <span className="text-[11px] text-slate-400">({pct}%)</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 3. COURBE TEMPORELLE / LINE */}
      {chart_type === 'line' && (
        <div className="pt-2 space-y-3">
          <div className="h-44 w-full relative">
            <svg viewBox="0 0 500 150" className="w-full h-full overflow-visible">
              <defs>
                <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Grid Lines */}
              <line x1="0" y1="20" x2="500" y2="20" stroke="#f1f5f9" strokeWidth="1" />
              <line x1="0" y1="75" x2="500" y2="75" stroke="#f1f5f9" strokeWidth="1" />
              <line x1="0" y1="130" x2="500" y2="130" stroke="#e2e8f0" strokeWidth="1" />

              {/* Line and Area Path */}
              {(() => {
                if (series.length < 2) return null
                const points = series.map((s, idx) => {
                  const x = (idx / (series.length - 1)) * 480 + 10
                  const y = 130 - (s.value / maxValue) * 100
                  return { x, y }
                })

                const linePath = points.reduce((acc, p, idx) => `${acc} ${idx === 0 ? 'M' : 'L'} ${p.x} ${p.y}`, '')
                const areaPath = `${linePath} L ${points[points.length - 1].x} 130 L ${points[0].x} 130 Z`

                return (
                  <>
                    <path d={areaPath} fill="url(#lineGrad)" />
                    <path d={linePath} fill="none" stroke="#10b981" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                    {points.map((p, idx) => (
                      <g key={idx}>
                        <circle cx={p.x} cy={p.y} r="4.5" fill="#ffffff" stroke="#10b981" strokeWidth="2" />
                        <text x={p.x} y={p.y - 8} textAnchor="middle" className="text-[10px] font-bold fill-slate-700">{series[idx].value}</text>
                      </g>
                    ))}
                  </>
                )
              })()}
            </svg>
          </div>

          {/* Time Labels */}
          <div className="flex justify-between items-center px-2 text-[11px] text-slate-400 font-mono border-t border-slate-100 pt-1.5">
            {series.map((s, idx) => (
              <span key={idx}>{s.label}</span>
            ))}
          </div>
          {y_label && <p className="text-[10px] text-slate-400 text-right italic">{y_label}</p>}
        </div>
      )}
    </div>
  )
}
