import { Outlet } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";

export default function AppLayout() {

    return (

        <div className="flex h-screen bg-slate-950 text-white">

            <Sidebar />

            <div className="flex flex-col flex-1 overflow-hidden">

                <Topbar />

                <main className="flex-1 overflow-y-auto p-8">

                    <Outlet />

                </main>

            </div>

        </div>

    );

}