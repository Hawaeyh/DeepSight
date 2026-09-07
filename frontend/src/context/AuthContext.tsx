import { useEffect, useMemo, useState } from "react";

import api, { ensureGuestSession, resetUnauthorizedState, setUnauthorizedHandler } from "../services/api";
import type { AuthResponse, AuthUser } from "../types/auth";
import { AuthContext } from "./auth-context";
import { firebaseConfigured, firebaseEmailLogin, firebaseEmailRegister, firebaseGoogleLogin as signInFirebaseGoogle, firebaseLogout, observeFirebaseToken, restoredFirebaseUser } from "../services/firebaseAuth";

let restorationRequest: Promise<AuthUser> | null = null;

function restoreAuthenticatedUser(): Promise<AuthUser> {
    if (!restorationRequest) {
        restorationRequest = api.get<AuthUser>("/auth/me").then(response => response.data).finally(() => {
            restorationRequest = null;
        });
    }
    return restorationRequest;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [authStatus, setAuthStatus] = useState<"loading" | "authenticated" | "unauthenticated">("loading");

    useEffect(() => {
        let active = true;
        const token = localStorage.getItem("deepsight-access-token");
        if (!token) {
            restoredFirebaseUser().then(async firebaseUser => {
                if (!firebaseUser) throw new Error("No Firebase session");
                const response = await api.post<AuthResponse>("/auth/firebase", { id_token: await firebaseUser.getIdToken() });
                if (active) accept(response.data);
            }).catch(() => ensureGuestSession().catch(() => undefined).finally(() => { if (active) setAuthStatus("unauthenticated"); }));
            return () => { active = false; };
        }
        restoreAuthenticatedUser().then(restoredUser => {
            if (!active) return;
            setUser(restoredUser);
            setAuthStatus("authenticated");
        }).catch(() => {
            localStorage.removeItem("deepsight-access-token");
            if (active) { setUser(null); setAuthStatus("unauthenticated"); }
        });
        return () => { active = false; };
    }, []);

    useEffect(() => observeFirebaseToken(firebaseUser => {
        if (!firebaseUser || authStatus !== "authenticated") return;
        void firebaseUser.getIdToken().then(idToken => api.post<AuthResponse>("/auth/firebase", { id_token: idToken })).then(response => accept(response.data)).catch(() => logout());
    }), [authStatus]);

    useEffect(() => {
        setUnauthorizedHandler(() => {
            setUser(null);
            setAuthStatus("unauthenticated");
            void ensureGuestSession();
            const protectedPrefixes = ["/dashboard", "/history", "/reports", "/settings", "/profile", "/video", "/live", "/extension", "/admin"];
            if (protectedPrefixes.some(path => window.location.pathname === path || window.location.pathname.startsWith(`${path}/`))) {
                window.history.replaceState({}, "", "/login");
                window.dispatchEvent(new PopStateEvent("popstate"));
            }
        });
        return () => setUnauthorizedHandler(null);
    }, []);

    function accept(response: AuthResponse) {
        localStorage.setItem("deepsight-access-token", response.access_token);
        resetUnauthorizedState();
        setUser(response.user);
        setAuthStatus("authenticated");
    }

    async function login(email: string, password: string) {
        const response = await api.post<AuthResponse>("/auth/login", { email, password });
        accept(response.data);
        return response.data;
    }

    async function register(fullName: string, email: string, password: string) {
        const response = await api.post<AuthResponse>("/auth/register", { full_name: fullName, email, password });
        accept(response.data);
        return response.data;
    }

    async function googleLogin(credential: string) {
        const response = await api.post<AuthResponse>("/auth/google", { credential });
        accept(response.data);
        return response.data;
    }

    async function exchangeFirebaseUser(firebaseUser: { getIdToken(forceRefresh?: boolean): Promise<string> }) {
        const response = await api.post<AuthResponse>("/auth/firebase", { id_token: await firebaseUser.getIdToken(true) });
        accept(response.data);
        return response.data;
    }

    async function firebaseLogin(email: string, password: string) {
        return exchangeFirebaseUser(await firebaseEmailLogin(email, password));
    }

    async function firebaseGoogleLogin() {
        return exchangeFirebaseUser(await signInFirebaseGoogle());
    }

    async function firebaseRegister(email: string, password: string) {
        await firebaseEmailRegister(email, password);
    }

    function logout() {
        localStorage.removeItem("deepsight-access-token");
        setUser(null);
        setAuthStatus("unauthenticated");
        void ensureGuestSession();
        void firebaseLogout();
    }

    const loading = authStatus === "loading";
    const value = useMemo(() => ({ user, authStatus, loading, login, register, googleLogin, firebaseLogin, firebaseGoogleLogin, firebaseRegister, firebaseConfigured, logout }), [user, authStatus, loading]);
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
