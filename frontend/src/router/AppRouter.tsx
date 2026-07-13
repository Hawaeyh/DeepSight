import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Spinner from "../components/ui/Spinner";
import { useAuth } from "../context/AuthContext";
import HistoryPage from "../features/history/pages/HistoryPage";
import ImageDetectionPage from "../features/image/pages/ImageDetectionPage";
import AppLayout from "../layouts/AppLayout";
import AdminModelReportsPage from "../pages/AdminModelReportsPage";
import AdminUsersPage from "../pages/AdminUsersPage";
import DashboardPage from "../pages/DashboardPage";
import ExtensionPage from "../pages/ExtensionPage";
import LiveDetectionPage from "../pages/LiveDetectionPage";
import LoginPage from "../pages/LoginPage";
import PlansPage from "../pages/PlansPage";
import ProfilePage from "../pages/ProfilePage";
import RegisterPage from "../pages/RegisterPage";
import ReportsPage from "../pages/ReportsPage";
import SettingsPage from "../pages/SettingsPage";
import UserDashboardPage from "../pages/UserDashboardPage";
import VideoDetectionPage from "../pages/VideoDetectionPage";
import WelcomePage from "../pages/WelcomePage";

function LoadingScreen() {
    return <div className="flex h-screen items-center justify-center bg-slate-950"><Spinner /></div>;
}

function AuthenticatedRoute({ children }: { children: ReactNode }) {
    const { user, loading } = useAuth();
    if (loading) return <LoadingScreen />;
    return user ? children : <Navigate to="/login" replace />;
}

function AdminRoute({ children }: { children: ReactNode }) {
    const { user, loading } = useAuth();
    if (loading) return <LoadingScreen />;
    return user?.role === "admin" ? children : <Navigate to={user ? "/dashboard" : "/login"} replace />;
}

function PlanRoute({ minimum, children }: { minimum: "basic" | "lite"; children: ReactNode }) {
    const { user, loading } = useAuth();
    if (loading) return <LoadingScreen />;
    if (!user) return <Navigate to="/login" replace />;
    if (user.role === "admin") return children;
    const levels = { starter: 0, basic: 1, lite: 2 };
    return (levels[user.plan as keyof typeof levels] ?? 0) >= levels[minimum] ? children : <Navigate to="/plans" replace />;
}

export default function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<WelcomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                <Route element={<AppLayout />}>
                    <Route path="/image" element={<ImageDetectionPage />} />
                    <Route path="/plans" element={<PlansPage />} />
                    <Route path="/dashboard" element={<AuthenticatedRoute><UserDashboardPage /></AuthenticatedRoute>} />
                    <Route path="/video" element={<AuthenticatedRoute><VideoDetectionPage /></AuthenticatedRoute>} />
                    <Route path="/history" element={<AuthenticatedRoute><HistoryPage /></AuthenticatedRoute>} />
                    <Route path="/reports" element={<AuthenticatedRoute><ReportsPage /></AuthenticatedRoute>} />
                    <Route path="/settings" element={<AuthenticatedRoute><SettingsPage /></AuthenticatedRoute>} />
                    <Route path="/profile" element={<AuthenticatedRoute><ProfilePage /></AuthenticatedRoute>} />
                    <Route path="/extension" element={<PlanRoute minimum="basic"><ExtensionPage /></PlanRoute>} />
                    <Route path="/live" element={<PlanRoute minimum="lite"><LiveDetectionPage /></PlanRoute>} />
                    <Route path="/admin" element={<AdminRoute><DashboardPage /></AdminRoute>} />
                    <Route path="/admin/model-reports" element={<AdminRoute><AdminModelReportsPage /></AdminRoute>} />
                    <Route path="/admin/users" element={<AdminRoute><AdminUsersPage /></AdminRoute>} />
                </Route>

                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}
