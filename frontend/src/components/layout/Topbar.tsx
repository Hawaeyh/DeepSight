import {
    Bell,
    Search,
    UserCircle2,
} from "lucide-react";

export default function Topbar() {

    return (

        <header className="h-20 border-b border-slate-800 bg-slate-900 flex items-center justify-between px-8">

            <div>

                <h2 className="text-2xl font-bold">

                    AI-Powered Deepfake Detection

                </h2>

                <p className="text-slate-400 text-sm">

                    ML7-VIDS DeepSight System

                </p>

            </div>

            <div className="flex items-center gap-6">

                <Search
                    className="cursor-pointer hover:text-cyan-400"
                />

                <Bell
                    className="cursor-pointer hover:text-cyan-400"
                />

                <UserCircle2
                    size={36}
                    className="cursor-pointer hover:text-cyan-400"
                />

            </div>

        </header>

    );

}