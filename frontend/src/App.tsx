import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, MessageSquare, History, Globe, BarChart2 } from 'lucide-react';
import type { Lang, League, Team, Session, Message } from './types';
import { translations } from './i18n';
import { fetchLeaguesFromApi, fetchTeamsFromApi, API_BASE } from './api';
import { PredictPanel } from './components/PredictPanel';
import { ChatPanel } from './components/ChatPanel';

type Tab = 'predict' | 'chat';

function App() {
  const [lang, setLang] = useState<Lang>('es');
  const t = (key: string) => translations[lang][key] ?? key;

  const [activeTab, setActiveTab] = useState<Tab>('predict');
  const [leagues, setLeagues] = useState<League[]>([]);
  const [leaguesLoading, setLeaguesLoading] = useState(true);
  const [selectedLeague, setSelectedLeague] = useState('');
  const [teams, setTeams] = useState<Team[]>([]);
  const [teamsLoading, setTeamsLoading] = useState(false);
  const [team1, setTeam1] = useState<number | null>(null);
  const [team2, setTeam2] = useState<number | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [predictLoading, setPredictLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3500);
  };

  const welcomeMessage = (): Message => ({
    role: 'assistant',
    content: t('chatWelcome'),
  });

  useEffect(() => {
    loadLeagues();
    fetchSessions();
  }, []);

  useEffect(() => {
    if (!currentSessionId) {
      setMessages([welcomeMessage()]);
    }
  }, [lang, currentSessionId]);

  useEffect(() => {
    if (selectedLeague) {
      loadTeams(selectedLeague);
    } else {
      setTeams([]);
      setTeam1(null);
      setTeam2(null);
    }
  }, [selectedLeague]);

  useEffect(() => {
    if (currentSessionId) fetchMessages(currentSessionId);
  }, [currentSessionId]);

  const loadLeagues = async () => {
    setLeaguesLoading(true);
    try {
      setLeagues(await fetchLeaguesFromApi());
    } catch {
      showToast(t('errorChatting'));
      setLeagues([]);
    } finally {
      setLeaguesLoading(false);
    }
  };

  const loadTeams = async (competitionCode: string) => {
    setTeamsLoading(true);
    setTeam1(null);
    setTeam2(null);
    try {
      setTeams(await fetchTeamsFromApi(competitionCode));
    } catch {
      showToast(t('errorChatting'));
      setTeams([]);
    } finally {
      setTeamsLoading(false);
    }
  };

  const fetchSessions = async () => {
    try {
      const res = await axios.get(`${API_BASE}/sessions`);
      setSessions(res.data);
    } catch {
      /* silent */
    }
  };

  const fetchMessages = async (sessionId: number) => {
    try {
      const res = await axios.get(`${API_BASE}/sessions/${sessionId}/messages`);
      setMessages(res.data.length ? res.data : [welcomeMessage()]);
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        handleNewChat();
        fetchSessions();
      }
    }
  };

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([welcomeMessage()]);
    setTeam1(null);
    setTeam2(null);
    setSelectedLeague('');
    setTeams([]);
    setActiveTab('predict');
  };

  const handleSwapTeams = () => {
    setTeam1(team2);
    setTeam2(team1);
  };

  const handlePredict = async () => {
    if (!selectedLeague || !team1 || !team2) return;
    if (team1 === team2) {
      showToast(t('differentTeams'));
      return;
    }

    setPredictLoading(true);
    setActiveTab('predict');

    try {
      const res = await axios.post(`${API_BASE}/predict`, {
        competition_id: selectedLeague,
        team1_id: team1,
        team2_id: team2,
        session_id: currentSessionId,
        language: lang,
      });

      if (!currentSessionId) {
        setCurrentSessionId(res.data.session_id);
        fetchSessions();
      }
      await fetchMessages(res.data.session_id);
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        showToast(t('sessionExpired'));
        handleNewChat();
        fetchSessions();
      } else {
        showToast(t('errorAnalyzing'));
      }
    } finally {
      setPredictLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMsg: Message = { role: 'user', content: chatInput };
    setMessages((prev) => [...prev, userMsg]);
    const currentInput = chatInput;
    setChatInput('');
    setChatLoading(true);
    setActiveTab('chat');

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        message: currentInput,
        session_id: currentSessionId,
        language: lang,
      });

      if (!currentSessionId) {
        setCurrentSessionId(res.data.session_id);
        fetchSessions();
      }
      await fetchMessages(res.data.session_id);
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        showToast(t('sessionNotExists'));
        handleNewChat();
        fetchSessions();
      } else {
        setMessages((prev) => [...prev, { role: 'assistant', content: t('errorChatting') }]);
      }
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#0b1220] text-slate-200 overflow-hidden font-sans">
      {/* Sessions sidebar */}
      <aside className="w-56 shrink-0 bg-[#0f172a] border-r border-slate-800 flex flex-col hidden md:flex">
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-2 mb-4">
            <BarChart2 className="w-5 h-5 text-emerald-400" />
            <span className="font-bold text-white text-sm">{t('appTitle')}</span>
          </div>
          <button
            onClick={handleNewChat}
            className="flex items-center justify-center gap-2 w-full p-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition-colors"
          >
            <Plus className="w-4 h-4" /> {t('newAnalysis')}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          <p className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider px-2 py-2">
            <History className="w-3 h-3" /> {t('recentHistory')}
          </p>
          {sessions.length === 0 && (
            <p className="text-xs text-slate-600 px-2 py-4">{t('emptyChat')}</p>
          )}
          {sessions.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setCurrentSessionId(s.id);
                setActiveTab('chat');
              }}
              className={`w-full text-left p-2.5 rounded-xl truncate transition-all text-sm ${
                currentSessionId === s.id
                  ? 'bg-slate-800 text-emerald-400 ring-1 ring-emerald-500/30'
                  : 'text-slate-400 hover:bg-slate-800/80 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2">
                <MessageSquare className="w-3.5 h-3.5 shrink-0" />
                <span className="truncate">{s.title}</span>
              </div>
            </button>
          ))}
        </div>

        <div className="p-3 border-t border-slate-800">
          <button
            onClick={() => setLang((p) => (p === 'en' ? 'es' : 'en'))}
            className="flex items-center justify-center gap-2 w-full p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-sm transition-colors"
          >
            <Globe className="w-4 h-4 text-emerald-400" />
            {t('langToggle')}
          </button>
        </div>
      </aside>

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="shrink-0 flex items-center gap-2 px-4 py-3 border-b border-slate-800 bg-[#0f172a]/90">
          {(['predict', 'chat'] as Tab[]).map((tab) => {
            const isPredict = tab === 'predict';
            const active = activeTab === tab;
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  active
                    ? isPredict
                      ? 'bg-emerald-600/20 text-emerald-400 ring-1 ring-emerald-500/40'
                      : 'bg-sky-600/20 text-sky-400 ring-1 ring-sky-500/40'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50'
                }`}
              >
                {isPredict ? (
                  <BarChart2 className="w-4 h-4" />
                ) : (
                  <MessageSquare className="w-4 h-4" />
                )}
                {t(isPredict ? 'predictTab' : 'chatTab')}
              </button>
            );
          })}
        </header>

        <div className="flex-1 min-h-0">
          {activeTab === 'predict' ? (
            <PredictPanel
              lang={lang}
              leagues={leagues}
              leaguesLoading={leaguesLoading}
              teams={teams}
              teamsLoading={teamsLoading}
              selectedLeague={selectedLeague}
              team1={team1}
              team2={team2}
              loading={predictLoading}
              messages={messages}
              onLeagueChange={setSelectedLeague}
              onTeam1Change={setTeam1}
              onTeam2Change={setTeam2}
              onSwapTeams={handleSwapTeams}
              onPredict={handlePredict}
            />
          ) : (
            <ChatPanel
              lang={lang}
              messages={messages}
              loading={chatLoading}
              chatInput={chatInput}
              onChatInputChange={setChatInput}
              onSendMessage={handleSendMessage}
            />
          )}
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-5 py-3 rounded-xl bg-slate-800 border border-slate-600 text-sm text-white shadow-2xl">
          {toast}
        </div>
      )}
    </div>
  );
}

export default App;
