import { useEffect, useMemo, useState } from "react";
import { Activity, Search, ShieldCheck, UserCheck, Users } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import Spinner from "../components/ui/Spinner";
import api from "../services/api";
import type { AdminUsageAnalytics, AdminUser } from "../types/admin";

export default function AdminUsersPage() {
    const [users, setUsers] = useState<AdminUser[]>([]);
    const [analytics, setAnalytics] = useState<AdminUsageAnalytics | null>(null);
    const [loading, setLoading] = useState(true);
    const [busyId, setBusyId] = useState<number | null>(null);
    const [query, setQuery] = useState("");
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        Promise.all([
            api.get<AdminUser[]>("/admin/users"),
            api.get<AdminUsageAnalytics>("/admin/usage"),
        ]).then(([usersResponse, usageResponse]) => {
            setUsers(usersResponse.data);
            setAnalytics(usageResponse.data);
        }).catch(requestError => setError(requestError?.response?.data?.detail ?? "Unable to load administration data."))
            .finally(() => setLoading(false));
    }, []);

    const filteredUsers = useMemo(() => {
        const value = query.trim().toLowerCase();
        if (!value) return users;
        return users.filter(user => user.fullName.toLowerCase().includes(value) || user.email.toLowerCase().includes(value));
    }, [query, users]);

    async function updateUser(userId: number, changes: Partial<Pick<AdminUser, "role" | "plan" | "isActive">>) {
        try {
            setBusyId(userId);
            setError(null);
            const response = await api.patch<AdminUser>(`/admin/users/${userId}`, {
                role: changes.role,
                plan: changes.plan,
                is_active: changes.isActive,
            });
            setUsers(current => current.map(user => user.id === userId ? response.data : user));
        } catch (requestError: any) {
            setError(requestError?.response?.data?.detail ?? "Unable to update the account.");
        } finally {
            setBusyId(null);
        }
    }

    if (loading) return <div className="flex h-[60vh] items-center justify-center"><Spinner /></div>;

    return (
        <div className="space-y-6">
            <div>
                <p className="text-sm font-medium text-cyan-400">Administration</p>
                <h1 className="mt-1 text-3xl font-bold">Users and usage</h1>
                <p className="mt-2 text-sm text-slate-400">Account access, subscriptions, and registered-user detection activity.</p>
            </div>

            {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}

            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Summary icon={Users} label="Registered users" value={analytics?.totalUsers ?? 0} />
                <Summary icon={UserCheck} label="Active accounts" value={analytics?.activeUsers ?? 0} />
                <Summary icon={Activity} label="Total user runs" value={analytics?.totalRuns ?? 0} />
                <Summary icon={ShieldCheck} label="Runs in 14 days" value={analytics?.runsLast14Days ?? 0} />
            </section>

            <section className="grid gap-6 xl:grid-cols-3">
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 xl:col-span-2">
                    <h2 className="mb-5 font-semibold">User activity</h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={analytics?.trend ?? []} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="date" stroke="#94a3b8" tickFormatter={value => value.slice(5)} />
                                <YAxis stroke="#94a3b8" allowDecimals={false} />
                                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8 }} />
                                <Legend />
                                <Line type="monotone" dataKey="runs" name="Detection runs" stroke="#06b6d4" strokeWidth={2} />
                                <Line type="monotone" dataKey="activeUsers" name="Active users" stroke="#22c55e" strokeWidth={2} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                    <h2 className="mb-5 font-semibold">Users by plan</h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={analytics?.plans ?? []} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="plan" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" allowDecimals={false} />
                                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8 }} />
                                <Bar dataKey="users" name="Users" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </section>

            <section className="overflow-hidden rounded-lg border border-slate-800 bg-slate-900">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 px-5 py-4">
                    <h2 className="font-semibold">User management</h2>
                    <label className="relative w-full sm:w-72">
                        <Search className="absolute left-3 top-2.5 text-slate-500" size={18} />
                        <span className="sr-only">Search users</span>
                        <input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search name or email" className="w-full rounded-lg border border-slate-700 bg-slate-950 py-2 pl-10 pr-3 text-sm outline-none focus:border-cyan-500" />
                    </label>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[940px] text-left text-sm">
                        <thead className="bg-slate-800/60 text-slate-400"><tr><th className="px-5 py-3">User</th><th className="px-5 py-3">Role</th><th className="px-5 py-3">Plan</th><th className="px-5 py-3">Runs</th><th className="px-5 py-3">Last active</th><th className="px-5 py-3">Access</th></tr></thead>
                        <tbody className="divide-y divide-slate-800">
                            {filteredUsers.map(user => (
                                <tr key={user.id} className={busyId === user.id ? "opacity-60" : ""}>
                                    <td className="px-5 py-4"><span className="block font-medium">{user.fullName}</span><span className="text-xs text-slate-500">{user.email}</span></td>
                                    <td className="px-5 py-4"><select aria-label={`Role for ${user.fullName}`} disabled={busyId === user.id} value={user.role} onChange={event => updateUser(user.id, { role: event.target.value as AdminUser["role"] })} className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"><option value="user">User</option><option value="admin">Admin</option></select></td>
                                    <td className="px-5 py-4"><select aria-label={`Plan for ${user.fullName}`} disabled={busyId === user.id} value={user.plan} onChange={event => updateUser(user.id, { plan: event.target.value as AdminUser["plan"] })} className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"><option value="starter">Starter</option><option value="basic">Basic</option><option value="lite">Lite</option></select></td>
                                    <td className="px-5 py-4">{user.usageCount}</td>
                                    <td className="px-5 py-4 text-slate-400">{user.lastUsedAt ? new Date(user.lastUsedAt).toLocaleString() : "Never"}</td>
                                    <td className="px-5 py-4"><label className="inline-flex items-center gap-2"><input type="checkbox" checked={user.isActive} disabled={busyId === user.id} onChange={event => updateUser(user.id, { isActive: event.target.checked })} className="h-4 w-4 accent-cyan-500" /><span>{user.isActive ? "Active" : "Disabled"}</span></label></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {filteredUsers.length === 0 && <p className="p-8 text-center text-sm text-slate-500">No matching users.</p>}
                </div>
            </section>
        </div>
    );
}

function Summary({ icon: Icon, label, value }: { icon: typeof Users; label: string; value: number }) {
    return <div className="rounded-lg border border-slate-800 bg-slate-900 p-5"><div className="flex items-center gap-3 text-sm text-slate-400"><Icon size={19} />{label}</div><p className="mt-3 text-3xl font-bold">{value.toLocaleString()}</p></div>;
}
