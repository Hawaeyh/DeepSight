import { useEffect, useMemo, useState } from "react";
import { Bell, LogIn, LogOut, Menu, Search, Settings, UserCircle2, X } from "lucide-react";
import { useNavigate } from "react-router-dom";

import api from "../../services/api";
import type { Analysis } from "../../types/analysis";
import { useAuth } from "../../hooks/useAuth";

export default function Topbar({ onMenuToggle }: { onMenuToggle: () => void }) {
    const navigate = useNavigate();
    const { user, authStatus, logout } = useAuth();
    const [analyses, setAnalyses] = useState<Analysis[]>([]);
    const [notifications, setNotifications] = useState<Array<{id:number; title:string; message:string; isRead:boolean; createdAt:string}>>([]);
    const [query, setQuery] = useState("");
    const [searchOpen, setSearchOpen] = useState(false);
    const [notificationsOpen, setNotificationsOpen] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);

    useEffect(() => {
        if (authStatus !== "authenticated") {
            setAnalyses([]); setNotifications([]);
            return;
        }
        const load = () => Promise.all([api.get<Analysis[]>("/history"), api.get<Array<{id:number; title:string; message:string; isRead:boolean; createdAt:string}>>("/notifications")]).then(([history, alerts]) => { setAnalyses(history.data); setNotifications(alerts.data); }).catch(() => undefined);
        load();
        const timer = window.setInterval(load, 30000);
        return () => window.clearInterval(timer);
    }, [authStatus]);

    const results = useMemo(() => {
        const normalized = query.trim().toLowerCase();
        if (!normalized) return [];
        return analyses.filter(item =>
            item.filename.toLowerCase().includes(normalized)
            || item.prediction.toLowerCase().includes(normalized)
            || item.model_name.toLowerCase().includes(normalized)
        ).slice(0, 6);
    }, [analyses, query]);

    const unread = notifications.filter(item => !item.isRead).length;
    const profile = JSON.parse(localStorage.getItem("deepsight-profile") ?? "{}") as { fullName?: string; email?: string };
    const displayName = user?.full_name ?? profile.fullName ?? "Guest User";
    const displayEmail = user?.email ?? profile.email ?? "2 free detections daily";

    function openNotifications() {
        setNotificationsOpen(value => !value);
        setSearchOpen(false);
        setProfileOpen(false);
        if (!notificationsOpen && unread) {
            void api.post("/notifications/read-all").then(() => setNotifications(items => items.map(item => ({ ...item, isRead: true }))));
        }
    }

    function openHistory(item: Analysis) {
        navigate(`/history?search=${encodeURIComponent(item.filename)}`);
        setSearchOpen(false);
        setNotificationsOpen(false);
    }

    return (
        <header className="relative z-30 flex min-h-20 items-center justify-between border-b border-slate-800 bg-slate-900 px-5 md:px-8">
            <div className="flex min-w-0 items-center gap-3">
                <button type="button" aria-label="Toggle sidebar" title="Toggle sidebar" onClick={onMenuToggle} className="shrink-0 rounded-lg p-2 hover:bg-slate-800 hover:text-cyan-400">
                    <Menu size={23} />
                </button>
                <div className="min-w-0">
                    <h2 className="truncate text-lg font-bold md:text-2xl">DeepSight System</h2>
                    <p className="hidden text-sm text-slate-400 sm:block">Machine Learning-Driven Deepfake Image Detection System</p>
                </div>
            </div>

            <div className="flex items-center gap-2 md:gap-4">
                <button type="button" aria-label="Search analyses" title="Search analyses" onClick={() => { setSearchOpen(value => !value); setNotificationsOpen(false); setProfileOpen(false); }} className="rounded-lg p-2 hover:bg-slate-800 hover:text-cyan-400">
                    {searchOpen ? <X size={22} /> : <Search size={22} />}
                </button>
                <button type="button" aria-label="Notifications" title="Notifications" onClick={openNotifications} className="relative rounded-lg p-2 hover:bg-slate-800 hover:text-cyan-400">
                    <Bell size={22} />
                    {unread > 0 && <span className="absolute right-0 top-0 min-w-4 rounded-full bg-red-500 px-1 text-center text-[10px] font-bold">{Math.min(unread, 99)}</span>}
                </button>
                <button type="button" aria-label="Profile" title="Profile" onClick={() => { setProfileOpen(value => !value); setSearchOpen(false); setNotificationsOpen(false); }} className="rounded-lg p-1.5 hover:bg-slate-800 hover:text-cyan-400">
                    <UserCircle2 size={30} />
                </button>
            </div>

            {searchOpen && (
                <div className="absolute right-4 top-[calc(100%+8px)] w-[min(92vw,420px)] rounded-lg border border-slate-700 bg-slate-900 p-3 shadow-2xl">
                    <div className="relative">
                        <Search className="absolute left-3 top-3 text-slate-500" size={18} />
                        <input autoFocus value={query} onChange={event => setQuery(event.target.value)} placeholder="Filename, prediction, or model" className="w-full rounded-lg border border-slate-700 bg-slate-950 py-2.5 pl-10 pr-3 outline-none focus:border-cyan-500" />
                    </div>
                    <div className="mt-2 max-h-72 overflow-y-auto">
                        {query && results.length === 0 && <p className="p-4 text-center text-sm text-slate-500">No matching analyses.</p>}
                        {results.map(item => (
                            <button key={item.id} type="button" onClick={() => openHistory(item)} className="flex w-full items-center justify-between gap-3 rounded-lg p-3 text-left hover:bg-slate-800">
                                <span className="min-w-0"><span className="block truncate font-medium">{item.filename}</span><span className="text-xs text-slate-400">{item.model_name} · {new Date(item.created_at).toLocaleDateString()}</span></span>
                                <span className={item.prediction === "Fake" ? "text-red-400" : "text-green-400"}>{item.prediction}</span>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {notificationsOpen && (
                <div className="absolute right-4 top-[calc(100%+8px)] w-[min(92vw,380px)] rounded-lg border border-slate-700 bg-slate-900 p-3 shadow-2xl">
                    <div className="px-2 py-2 font-semibold">Notifications</div>
                    <div className="max-h-80 overflow-y-auto">
                        {notifications.slice(0, 8).map(item => (
                            <div key={item.id} className="flex w-full gap-3 rounded-lg p-3 text-left">
                                <span className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${item.isRead ? "bg-slate-600" : "bg-cyan-400"}`} />
                                <span className="min-w-0"><span className="block truncate font-medium">{item.title}</span><span className="text-xs text-slate-400">{item.message} · {new Date(item.createdAt).toLocaleString()}</span></span>
                            </div>
                        ))}
                        {notifications.length === 0 && <p className="p-4 text-sm text-slate-500">No notifications yet.</p>}
                    </div>
                </div>
            )}

            {profileOpen && (
                <div className="absolute right-4 top-[calc(100%+8px)] w-72 rounded-lg border border-slate-700 bg-slate-900 p-3 shadow-2xl">
                    <div className="border-b border-slate-800 px-3 py-3"><div className="font-semibold">{displayName}</div><div className="mt-1 truncate text-sm text-slate-400">{displayEmail}</div></div>
                    <button type="button" onClick={() => { navigate("/profile"); setProfileOpen(false); }} className="mt-2 flex w-full items-center gap-3 rounded-lg p-3 text-left hover:bg-slate-800"><UserCircle2 size={19} />Profile</button>
                    <button type="button" onClick={() => { navigate("/settings"); setProfileOpen(false); }} className="flex w-full items-center gap-3 rounded-lg p-3 text-left hover:bg-slate-800"><Settings size={19} />Settings</button>
                    {user ? (
                        <button type="button" onClick={() => { logout(); navigate("/"); setProfileOpen(false); }} className="flex w-full items-center gap-3 rounded-lg p-3 text-left text-red-300 hover:bg-slate-800"><LogOut size={19} />Sign Out</button>
                    ) : (
                        <button type="button" onClick={() => { navigate("/login"); setProfileOpen(false); }} className="flex w-full items-center gap-3 rounded-lg p-3 text-left text-cyan-300 hover:bg-slate-800"><LogIn size={19} />Sign In</button>
                    )}
                </div>
            )}
        </header>
    );
}
