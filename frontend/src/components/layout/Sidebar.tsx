import {
    BarChart3,
    ChevronLeft,
    ChevronRight,
    CreditCard,
    FileChartColumn,
    FileText,
    History,
    Home,
    Image,
    Settings,
    Video,
    Users,
    Radio,
    ScanSearch,
} from "lucide-react";
import { NavLink } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import UsageWidget from "../subscription/UsageWidget";

const publicMenus = [
    { title: "Welcome", path: "/", icon: Home },
    { title: "Test Image", path: "/image", icon: Image },
    { title: "Plans", path: "/plans", icon: CreditCard },
];

const userMenus = [
    { title: "Dashboard", path: "/dashboard", icon: Home },
    { title: "Image Detection", path: "/image", icon: Image },
    { title: "Video Detection", path: "/video", icon: Video },
    { title: "History", path: "/history", icon: History },
    { title: "Reports", path: "/reports", icon: FileText },
    { title: "Plans", path: "/plans", icon: CreditCard },
    { title: "Settings", path: "/settings", icon: Settings },
];

const adminMenus = [
    { title: "Admin Analytics", path: "/admin", icon: BarChart3 },
    { title: "All Analyses", path: "/admin/analyses", icon: History },
    { title: "Model Reports", path: "/admin/model-reports", icon: FileChartColumn },
    { title: "User Management", path: "/admin/users", icon: Users },
];

interface SidebarProps {
    collapsed: boolean;
    onToggle: () => void;
}

export default function Sidebar({ collapsed, onToggle }: SidebarProps) {
    const { user } = useAuth();
    const subscriptionMenus = user?.role === "admin" || user?.plan === "lite"
        ? [{ title: "Extension Pro", path: "/extension", icon: ScanSearch }, { title: "Live Detection", path: "/live", icon: Radio }]
        : user?.plan === "basic"
            ? [{ title: "Extension", path: "/extension", icon: ScanSearch }]
            : [];
    const accountMenus = user ? [...userMenus, ...subscriptionMenus] : publicMenus;
    const menus = user?.role === "admin" ? [...accountMenus, ...adminMenus] : accountMenus;

    return (
        <aside className={`${collapsed ? "w-20" : "w-72"} flex shrink-0 flex-col border-r border-slate-800 bg-slate-900 transition-[width] duration-200`}>
            <div className={`flex h-20 items-center border-b border-slate-800 ${collapsed ? "justify-center px-3" : "justify-between px-5"}`}>
                <div className="flex min-w-0 items-center gap-3">
                    <img src="/deepsight-logo.png" alt="DeepSight System logo" className="h-10 w-10 shrink-0 rounded-lg object-cover" />
                    {!collapsed && <h1 className="truncate text-lg font-bold text-cyan-400">DeepSight System</h1>}
                </div>
                {!collapsed && (
                    <button type="button" onClick={onToggle} aria-label="Close sidebar" title="Close sidebar" className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white">
                        <ChevronLeft size={20} />
                    </button>
                )}
            </div>

            {collapsed && (
                <button type="button" onClick={onToggle} aria-label="Open sidebar" title="Open sidebar" className="mx-auto mt-3 rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white">
                    <ChevronRight size={20} />
                </button>
            )}

            <nav className={`${collapsed ? "px-3" : "px-4"} flex-1 overflow-y-auto py-4`}>
                {menus.map(menu => (
                    <NavLink
                        key={menu.path}
                        to={menu.path}
                        end={menu.path === "/" || menu.path === "/admin" || menu.path === "/dashboard"}
                        title={collapsed ? menu.title : undefined}
                        className={({ isActive }) => `mb-2 flex h-11 items-center rounded-lg transition-colors ${collapsed ? "justify-center px-2" : "gap-3 px-4"} ${isActive ? "bg-cyan-500 text-white" : "text-slate-300 hover:bg-slate-800"}`}
                    >
                        <menu.icon size={20} className="shrink-0" />
                        {!collapsed && <span className="truncate">{menu.title}</span>}
                    </NavLink>
                ))}
            </nav>

            {!collapsed && <UsageWidget />}
            {!collapsed && <div className="border-t border-slate-800 px-6 py-4 text-xs text-slate-500">DeepSight System v2.0</div>}
        </aside>
    );
}
