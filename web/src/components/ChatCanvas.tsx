'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, User } from 'lucide-react'
import { marked } from 'marked'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ChatCanvasProps {
  onMessageSent: (message: string) => void
  activeConversationId: string | null
  setActiveConversationId: (id: string) => void
}

export const ChatCanvas: React.FC<ChatCanvasProps> = ({ onMessageSent, activeConversationId, setActiveConversationId }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const chatAreaRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || inputValue.trim()
    if (!text || isLoading) return

    setInputValue('')
    onMessageSent(text)

    const userMsg: Message = {
      id: 'user-' + Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_AXORA_API_URL || 'http://localhost:8000/api/v1'
      const resp = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          conversation_id: activeConversationId,
        }),
      })

      const data = await resp.json()
      if (data.conversation_id) {
        setActiveConversationId(data.conversation_id)
      }

      const agentMsg: Message = {
        id: 'agent-' + Date.now(),
        role: 'assistant',
        content: data.response || 'Traitement effectué.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }

      setMessages((prev) => [...prev, agentMsg])
    } catch (err: any) {
      const errorMsg: Message = {
        id: 'err-' + Date.now(),
        role: 'assistant',
        content: "Une erreur est survenue lors de la communication avec l'Agent Axora : " + err.message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="flex-1 flex flex-col overflow-y-auto px-8 py-6 space-y-6" ref={chatAreaRef}>
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Assistant Axora</h1>
        <p className="text-xs text-slate-500 max-w-3xl leading-relaxed">
          Posez vos questions en langage naturel. L'agent analyse votre demande, explore le modèle métier et interroge les données pour vous fournir une réponse précise et fiable.
        </p>
      </div>

      <div className="flex-1 space-y-6">
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-full bg-[#1a56db] text-white flex items-center justify-center font-bold text-sm shadow">A</div>
            <div>
              <h3 className="text-xs font-bold text-slate-900">Bienvenue sur Axora Agent</h3>
              <p className="text-[11px] text-slate-500">Choisissez une suggestion ci-dessous ou saisissez votre intention métier.</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <button onClick={() => handleSend('Qui est Rasoa')} className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-700 rounded-lg transition">🔍 Qui est Rasoa ?</button>
            <button onClick={() => handleSend('Lister tous les membres')} className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-700 rounded-lg transition">👥 Lister tous les membres</button>
            <button onClick={() => handleSend("Quels sont les membres qui n'ont pas d'association ?")} className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-700 rounded-lg transition">🏷️ Membres sans association</button>
            <button onClick={() => handleSend('Lister tous les églises enregistrés')} className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-700 rounded-lg transition">⛪ Lister les églises</button>
          </div>
        </div>

        {messages.map((m) =>
          m.role === 'user' ? (
            <div key={m.id} className="flex items-start justify-end space-x-3 pt-2">
              <div className="flex flex-col items-end">
                <div className="bg-blue-50/80 border border-blue-100 rounded-2xl rounded-tr-none px-4 py-3 text-slate-800 text-sm shadow-xs font-medium">
                  {m.content}
                </div>
                <div className="flex items-center space-x-1 mt-1 mr-1 text-[11px] text-slate-400">
                  <span>{m.timestamp}</span>
                </div>
              </div>
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center flex-shrink-0 border border-blue-200">
                <User className="w-4 h-4" />
              </div>
            </div>
          ) : (
            <div key={m.id} className="flex items-start space-x-3.5">
              <div className="w-8 h-8 rounded-full bg-[#1a56db] text-white flex items-center justify-center font-bold text-sm shadow flex-shrink-0 ring-2 ring-blue-50">A</div>
              <div className="flex-1 bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span className="text-xs font-semibold text-slate-700">Réponse de l'Agent Axora</span>
                  </div>
                  <span className="text-[11px] text-slate-400">{m.timestamp}</span>
                </div>
                <div
                  className="prose prose-slate prose-sm text-xs leading-relaxed text-slate-800 max-w-none"
                  dangerouslySetInnerHTML={{ __html: marked.parse(m.content) as string }}
                />
              </div>
            </div>
          )
        )}

        {isLoading && (
          <div className="flex items-start space-x-3.5">
            <div className="w-8 h-8 rounded-full bg-[#1a56db] text-white flex items-center justify-center font-bold text-sm shadow flex-shrink-0 animate-pulse">A</div>
            <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs text-xs text-slate-500 flex items-center space-x-3">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-600"></span>
              </span>
              <span>Traitement de l'intention par le Runtime Agent...</span>
            </div>
          </div>
        )}
      </div>

      <div className="pt-2 sticky bottom-0 bg-[#f8fafc] pb-2">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="relative bg-white border border-slate-300 rounded-2xl shadow-sm focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 flex items-center px-3 py-2 transition"
        >
          <input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="flex-1 border-0 focus:ring-0 text-sm text-slate-800 placeholder-slate-400 px-3 py-1 bg-transparent focus:outline-none"
            placeholder="Écrivez votre intention métier (ex: Qui sont les membres d'Andoharanofotsy ?)..."
            type="text"
          />
          <button
            type="submit"
            className="w-9 h-9 bg-blue-600 hover:bg-blue-700 text-white rounded-xl flex items-center justify-center shadow transition flex-shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </section>
  )
}
