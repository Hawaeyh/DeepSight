import { useState } from "react";
import { CheckCircle2, UserCircle2 } from "lucide-react";

import Button from "../components/ui/Button";
import Card from "../components/ui/Card";

interface Profile {
    fullName: string;
    email: string;
    organization: string;
}

export default function ProfilePage() {
    const stored = JSON.parse(localStorage.getItem("deepsight-profile") ?? "{}") as Partial<Profile>;
    const [profile, setProfile] = useState<Profile>({
        fullName: stored.fullName ?? "",
        email: stored.email ?? "",
        organization: stored.organization ?? "",
    });
    const [saved, setSaved] = useState(false);

    function save(event: React.FormEvent) {
        event.preventDefault();
        localStorage.setItem("deepsight-profile", JSON.stringify(profile));
        setSaved(true);
        window.setTimeout(() => setSaved(false), 2000);
    }

    return (
        <div className="mx-auto max-w-3xl space-y-8">
            <div><h1 className="text-3xl font-bold">Profile</h1><p className="mt-2 text-slate-400">Manage the identity displayed in DeepSight.</p></div>
            <Card title="Personal Information" action={<UserCircle2 className="text-cyan-400" size={34} />}>
                <form className="space-y-5" onSubmit={save}>
                    <label className="block"><span className="mb-2 block text-sm text-slate-400">Full name</span><input required value={profile.fullName} onChange={event => setProfile({ ...profile, fullName: event.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3 outline-none focus:border-cyan-500" /></label>
                    <label className="block"><span className="mb-2 block text-sm text-slate-400">Email</span><input required type="email" value={profile.email} onChange={event => setProfile({ ...profile, email: event.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3 outline-none focus:border-cyan-500" /></label>
                    <label className="block"><span className="mb-2 block text-sm text-slate-400">Organization</span><input value={profile.organization} onChange={event => setProfile({ ...profile, organization: event.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3 outline-none focus:border-cyan-500" /></label>
                    <div className="flex items-center gap-4"><Button type="submit">Save Profile</Button>{saved && <span className="flex items-center gap-2 text-green-400"><CheckCircle2 size={18} />Saved</span>}</div>
                </form>
            </Card>
        </div>
    );
}
