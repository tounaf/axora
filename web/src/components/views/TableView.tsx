'use client'

import React, { useState, useMemo } from 'react'
import { ArrowUpDown, Download, Search } from 'lucide-react'

interface Column {
  key: string
  label: string
  data_type: 'string' | 'number' | 'date' | 'badge' | 'tags' | 'boolean'
  sortable?: boolean
}

interface TableViewProps {
  title?: string
  description?: string
  data: {
    entity?: string
    columns: Column[]
    rows: Record<string, any>[]
    total_count?: number
  }
}

export const TableView: React.FC<TableViewProps> = ({ title, description, data }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  const { columns = [], rows = [] } = data

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortOrder('asc')
    }
  }

  const filteredRows = useMemo(() => {
    return rows.filter((row) =>
      Object.values(row).some((val) =>
        String(val || '').toLowerCase().includes(searchTerm.toLowerCase())
      )
    )
  }, [rows, searchTerm])

  const sortedRows = useMemo(() => {
    if (!sortKey) return filteredRows
    return [...filteredRows].sort((a, b) => {
      const valA = a[sortKey]
      const valB = b[sortKey]
      if (valA === valB) return 0
      if (valA == null) return 1
      if (valB == null) return -1
      const res = String(valA).localeCompare(String(valB), undefined, { numeric: true })
      return sortOrder === 'asc' ? res : -res
    })
  }, [filteredRows, sortKey, sortOrder])

  const exportCSV = () => {
    if (!columns.length || !rows.length) return
    const headers = columns.map((c) => `"${c.label}"`).join(',')
    const csvRows = sortedRows.map((r) =>
      columns.map((c) => `"${Array.isArray(r[c.key]) ? r[c.key].join(', ') : (r[c.key] ?? '')}"`).join(',')
    )
    const blob = new Blob([headers + '\n' + csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title || 'export'}.csv`
    a.click()
  }

  const renderCell = (col: Column, val: any) => {
    if (val == null || val === '') return <span className="text-slate-300">-</span>

    if (col.data_type === 'badge') {
      const strVal = String(val)
      const isPositive = ['ACTIF', 'MARIE', 'APPROUVEE'].includes(strVal.toUpperCase())
      const isNeutral = ['CELIBATAIRE', 'EN_ATTENTE'].includes(strVal.toUpperCase())
      const badgeCls = isPositive
        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
        : isNeutral
        ? 'bg-blue-50 text-blue-700 border-blue-200'
        : 'bg-slate-100 text-slate-700 border-slate-200'

      return (
        <span className={`px-2 py-0.5 text-[10px] font-medium border rounded-full inline-block ${badgeCls}`}>
          {strVal}
        </span>
      )
    }

    if (col.data_type === 'tags' && Array.isArray(val)) {
      if (!val.length) return <span className="text-slate-400 italic text-[11px]">Aucune</span>
      return (
        <div className="flex flex-wrap gap-1">
          {val.map((item, idx) => (
            <span key={idx} className="px-2 py-0.5 bg-slate-100 text-slate-700 text-[10px] rounded font-medium">
              {item}
            </span>
          ))}
        </div>
      )
    }

    return <span>{String(val)}</span>
  }

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-xs space-y-2 mt-3">
      {/* Table Header Controls */}
      <div className="px-4 py-3 bg-slate-50/70 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h4 className="text-xs font-bold text-slate-900">{title || 'Tableau de Données'}</h4>
          {description && <p className="text-[11px] text-slate-500">{description}</p>}
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filtrer..."
              className="text-xs pl-8 pr-3 py-1 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 w-36"
            />
          </div>
          <button
            onClick={exportCSV}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-slate-700 transition"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            <span>CSV</span>
          </button>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50/50 border-b border-slate-200 text-slate-700 font-semibold">
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => col.sortable !== false && handleSort(col.key)}
                  className={`py-2 px-3 text-[11px] whitespace-nowrap ${col.sortable !== false ? 'cursor-pointer hover:bg-slate-100 transition' : ''}`}
                >
                  <div className="flex items-center gap-1">
                    <span>{col.label}</span>
                    {col.sortable !== false && <ArrowUpDown className="w-3 h-3 text-slate-400" />}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700 font-normal">
            {sortedRows.length > 0 ? (
              sortedRows.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60 transition">
                  {columns.map((col) => (
                    <td key={col.key} className="py-2.5 px-3 whitespace-nowrap">
                      {renderCell(col, row[col.key])}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="py-4 text-center text-slate-400 text-xs italic">
                  Aucun résultat correspondant.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="px-4 py-2 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-medium">
        <span>Total : {sortedRows.length} ligne(s)</span>
      </div>
    </div>
  )
}
