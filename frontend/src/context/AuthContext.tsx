import { createContext, useContext, useEffect, useMemo, useState } from "react";

import api from "../services/api";
import type { AuthResponse, AuthUser } from "../types/auth";

interface AuthContextValue {
    user: AuthUser | null;
    loading: boolean;
    login(email: string, password: string): Promise<void>;
    register(fullName: string, email: string, password: string): Promise<void>;
    googleLogin(credential: string): Promise<void>;
    logout(): void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!localStorage.getItem("deepsight-access-token")) {
            setLoading(false);
            return;
        }
        api.get<AuthUser>("/auth/me")
            .then(response => setUser(response.data))
            .catch(() => localStorage.removeItem("deepsight-access-token"))
            .finally(() => setLoading(false));
    }, []);

    function accept(response: AuthResponse) {
        localStorage.setItem("deepsight-access-token", response.access_token);
        setUser(response.user);
    }

    async function login(email: string, password: string) {
        const response = await api.post<AuthResponse>("/auth/login", { email, password });
        accept(response.data);
    }

    async function register(fullName: string, email: string, password: string) {
        const response = await api.post<AuthResponse>("/auth/register", { full_name: fullName, email, password });
        accept(response.data);
    }

    async function googleLogin(credential: string) {
        const response = await api.post<AuthResponse>("/auth/google", { credential });
        accept(response.data);
    }

    function logout() {
        localStorage.removeItem("deepsight-access-token");
        setUser(null);
    }

    const value = useMemo(() => ({ user, loading, login, register, googleLogin, logout }), [user, loading]);
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error("useAuth must be used within AuthProvider");
    return context;
}
