'use client'

import React, { useState } from 'react'
import { SidebarNav } from '@/components/SidebarNav'
import { TopHeader } from '@/components/TopHeader'
import { ChatCanvas } from '@/components/ChatCanvas'
import { ContextInspector } from '@/components/ContextInspector'

export default function Home() {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [lastQuerySummary, setLastQuerySummary] = useState<string>("Prêt à analyser vos intentions métier.")

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#f8fafc]">
      <SidebarNav onQuickAction={(msg) => setLastQuerySummary(msg)} />
      <div className="flex-1 flex flex-col min-w-0 bg-[#f8fafc] overflow-hidden">
        <TopHeader />
        <div className="flex-1 flex overflow-hidden">
          <ChatCanvas
            onMessageSent={(msg) => setLastQuerySummary(msg)}
            activeConversationId={activeConversationId}
            setActiveConversationId={setActiveConversationId}
          />
          <ContextInspector summary={lastQuerySummary} />
        </div>
      </div>
    </div>
  )
}
