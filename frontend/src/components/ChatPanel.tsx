import { useRef, useEffect, type FormEvent } from 'react';
import { Loader2, Send, MessageSquare } from 'lucide-react';
import type { Lang, Message } from '../types';
import { translations } from '../i18n';
import { PredictionCard } from './PredictionCard';
import { MarkdownContent } from './MarkdownContent';

interface ChatPanelProps {
  lang: Lang;
  messages: Message[];
  loading: boolean;
  chatInput: string;
  onChatInputChange: (value: string) => void;
  onSendMessage: (e: FormEvent) => void;
}

export function ChatPanel({
  lang,
  messages,
  loading,
  chatInput,
  onChatInputChange,
  onSendMessage,
}: ChatPanelProps) {
  const t = (key: string) => translations[lang][key] ?? key;
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const hasConversation = messages.some((m) => m.role === 'user');

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="shrink-0 px-6 py-4 border-b border-slate-800 bg-[#0f172a]/60">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-sky-400" />
          <div>
            <h2 className="text-lg font-bold text-white">{t('chatTab')}</h2>
            <p className="text-xs text-slate-500">{t('chatTabDesc')}</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-3xl mx-auto space-y-5">
          {!hasConversation && !loading && (
            <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/30 p-10 text-center">
              <MessageSquare className="w-10 h-10 text-sky-500/60 mx-auto mb-3" />
              <p className="text-slate-400 text-sm leading-relaxed">{t('chatWelcome')}</p>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl w-full ${m.role === 'user' ? 'max-w-lg' : ''}`}>
                <p
                  className={`text-[10px] font-bold uppercase tracking-wider mb-1.5 px-1 ${
                    m.role === 'user' ? 'text-right text-slate-500' : 'text-sky-400'
                  }`}
                >
                  {m.role === 'user' ? t('you') : t('assistant')}
                </p>
                {m.prediction_data ? (
                  <PredictionCard data={m.prediction_data} lang={lang} />
                ) : (
                  <div
                    className={`p-4 rounded-2xl text-sm leading-relaxed ${
                      m.role === 'user'
                        ? 'bg-sky-600 text-white rounded-br-md ml-auto'
                        : 'bg-slate-800/90 text-slate-200 border border-slate-700 rounded-bl-md'
                    }`}
                  >
                    {m.role === 'assistant' ? (
                      <MarkdownContent content={m.content} />
                    ) : (
                      m.content
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 p-4 rounded-2xl border border-slate-700 flex items-center gap-3">
                <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
                <span className="text-sm text-slate-400">{t('thinking')}</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </div>

      <footer className="shrink-0 p-4 md:p-5 border-t border-slate-800 bg-[#0f172a]/90">
        <form onSubmit={onSendMessage} className="max-w-3xl mx-auto flex gap-2">
          <input
            type="text"
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white outline-none focus:ring-2 focus:ring-sky-500 placeholder:text-slate-500"
            placeholder={t('chatPlaceholder')}
            value={chatInput}
            onChange={(e) => onChatInputChange(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !chatInput.trim()}
            className="px-5 py-3 rounded-xl bg-sky-600 hover:bg-sky-500 disabled:bg-slate-700 disabled:text-slate-500 font-semibold text-sm flex items-center gap-2 transition-colors"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">{t('send')}</span>
          </button>
        </form>
      </footer>
    </div>
  );
}
