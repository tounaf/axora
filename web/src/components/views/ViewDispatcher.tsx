'use client'

import React from 'react'
import { TableView } from './TableView'
import { ChartView } from './ChartView'
import { MetricCardView } from './MetricCardView'

export interface ViewPayload {
  view_type: string
  title?: string
  description?: string
  data: Record<string, any>
}

// Extensible registry pattern for frontend view components
const VIEW_COMPONENTS: Record<string, React.FC<any>> = {
  table: TableView,
  chart: ChartView,
  metric_cards: MetricCardView,
}

export function registerCustomView(viewType: string, component: React.FC<any>) {
  VIEW_COMPONENTS[viewType] = component
}

interface ViewDispatcherProps {
  view: ViewPayload | null
}

export const ViewDispatcher: React.FC<ViewDispatcherProps> = ({ view }) => {
  if (!view || !view.view_type) return null

  const Component = VIEW_COMPONENTS[view.view_type]

  if (!Component) {
    return (
      <div className="border border-amber-200 bg-amber-50 rounded-xl p-3 text-xs text-amber-800 mt-3">
        Vue &apos;{view.view_type}&apos; non supportée pour le moment.
      </div>
    )
  }

  return <Component title={view.title} description={view.description} data={view.data} />
}
