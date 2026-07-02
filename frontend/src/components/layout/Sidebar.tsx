import {
    LayoutDashboard,
    Image,
    Video,
    History,
    FileText,
    Settings,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const menus = [

    {
        title: "Dashboard",
        path: "/",
        icon: LayoutDashboard,
    },

    {
        title: "Image Detection",
        path: "/image",
        icon: Image,
    },

    {
        title: "Video Detection",
        path: "/video",
        icon: Video,
    },

    {
        title: "History",
        path: "/history",
        icon: History,
    },

    {
        title: "Reports",
        path: "/reports",
        icon: FileText,
    },

    {
        title: "Settings",
        path: "/settings",
        icon: Settings,
    },

];

export default function Sidebar() {

    return (

        <aside className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col">

            <div className="p-8">

                <h1 className="text-3xl font-bold text-cyan-400">

                    ML7-VIDS

                </h1>

                <p className="text-slate-400 mt-1">

                    DeepSight System

                </p>

            </div>

            <nav className="px-4 flex-1">

                {

                    menus.map((menu) => (

                        <NavLink

                            key={menu.title}

                            to={menu.path}

                            className={({ isActive }) =>

                                `flex items-center gap-3 rounded-xl px-4 py-3 mb-2 transition-all duration-200 ${
                                    isActive
                                        ? "bg-cyan-500 text-white"
                                        : "text-slate-300 hover:bg-slate-800"
                                }`
                            }

                        >

                            <menu.icon size={20} />

                            {menu.title}

                        </NavLink>

                    ))

                }

            </nav>

            <div className="p-6 border-t border-slate-800">

                <p className="text-sm text-slate-400">

                    Version

                </p>

                <p className="text-cyan-400 font-semibold">

                    DeepSight v2.0

                </p>

            </div>

        </aside>

    );

}