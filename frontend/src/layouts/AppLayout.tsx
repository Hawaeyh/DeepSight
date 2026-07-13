import { useState } from "react";
import { Outlet } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";

export default function AppLayout() {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(() => localStorage.getItem("deepsight-sidebar-collapsed") === "true");

    function toggleSidebar() {
        setSidebarCollapsed(current => {
            localStorage.setItem("deepsight-sidebar-collapsed", String(!current));
            return !current;
        });
    }

    return (

        <div className="flex h-screen bg-slate-950 text-white">

            <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />

            <div className="flex min-w-0 flex-1 flex-col overflow-hidden">

                <Topbar onMenuToggle={toggleSidebar} />

                <main className="flex-1 overflow-y-auto p-4 md:p-8">

                    <Outlet />

                </main>

            </div>

        </div>

    );

}
