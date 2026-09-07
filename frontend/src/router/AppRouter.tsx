import { lazy, Suspense } from "react";
import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Spinner from "../components/ui/Spinner";
import { useAuth } from "../hooks/useAuth";
import AppLayout from "../layouts/AppLayout";


const HistoryPage = lazy(() => import("../features/history/pages/HistoryPage"));
const ImageDetectionPage = lazy(() => import("../features/image/pages/ImageDetectionPage"));
const AdminModelReportsPage = lazy(() => import("../pages/AdminModelReportsPage"));
const AdminUsersPage = lazy(() => import("../pages/AdminUsersPage"));
const AdminAnalysesPage = lazy(() => import("../pages/AdminAnalysesPage"));
const DashboardPage = lazy(() => import("../pages/DashboardPage"));
const ExtensionPage = lazy(() => import("../pages/ExtensionPage"));
const LiveDetectionPage = lazy(() => import("../pages/LiveDetectionPage"));
const LoginPage = lazy(() => import("../pages/LoginPage"));
const PlansPage = lazy(() => import("../pages/PlansPage"));
const ProfilePage = lazy(() => import("../pages/ProfilePage"));
const RegisterPage = lazy(() => import("../pages/RegisterPage"));
const ReportsPage = lazy(() => import("../pages/ReportsPage"));
const SettingsPage = lazy(() => import("../pages/SettingsPage"));
const UserDashboardPage = lazy(() => import("../pages/UserDashboardPage"));
const VideoDetectionPage = lazy(() => import("../pages/VideoDetectionPage"));
const WelcomePage = lazy(() => import("../pages/WelcomePage"));
const SubscriptionSuccessPage = lazy(() => import("../pages/SubscriptionSuccessPage"));
const SubscriptionCancelPage = lazy(() => import("../pages/SubscriptionCancelPage"));


function LoadingScreen() {
    return <div className="flex h-screen items-center justify-center bg-slate-950"><Spinner /></div>;
}

function AuthenticatedRoute({ children }: { children: ReactNode }) {
    const { authStatus } = useAuth();
    if (authStatus === "loading") return <LoadingScreen />;
    return authStatus === "authenticated" ? children : <Navigate to="/login" replace />;
}

function AdminRoute({ children }: { children: ReactNode }) {
    const { user, authStatus } = useAuth();
    if (authStatus === "loading") return <LoadingScreen />;
    return user?.role === "admin" ? children : <Navigate to={user ? "/dashboard" : "/login"} replace />;
}

function PlanRoute({ minimum, children }: { minimum: "basic" | "lite"; children: ReactNode }) {
    const { user, authStatus } = useAuth();
    if (authStatus === "loading") return <LoadingScreen />;
    if (authStatus !== "authenticated" || !user) return <Navigate to="/login" replace />;
    if (user.role === "admin") return children;
    const levels = { starter: 0, basic: 1, lite: 2 };
    return (levels[user.plan as keyof typeof levels] ?? 0) >= levels[minimum] ? children : <Navigate to="/plans" replace />;
}

export default function AppRouter() {
    return (
        <BrowserRouter>
            <Suspense fallback={<LoadingScreen />}>
                <Routes>
                    <Route path="/" element={<WelcomePage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/subscription/success" element={<AuthenticatedRoute><SubscriptionSuccessPage /></AuthenticatedRoute>} />
                    <Route path="/subscription/cancel" element={<SubscriptionCancelPage />} />
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
                        <Route path="/admin/analyses" element={<AdminRoute><AdminAnalysesPage /></AdminRoute>} />
                    </Route>
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </Suspense>
        </BrowserRouter>
    );
}
