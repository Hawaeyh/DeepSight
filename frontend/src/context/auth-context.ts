import { createContext } from "react";

import type { AuthResponse, AuthUser } from "../types/auth";


export interface AuthContextValue {
    user: AuthUser | null;
    authStatus: "loading" | "authenticated" | "unauthenticated";
    loading: boolean;
    login(email: string, password: string): Promise<AuthResponse>;
    register(fullName: string, email: string, password: string): Promise<AuthResponse>;
    googleLogin(credential: string): Promise<AuthResponse>;
    firebaseLogin(email: string, password: string): Promise<AuthResponse>;
    firebaseGoogleLogin(): Promise<AuthResponse>;
    firebaseRegister(email: string, password: string): Promise<void>;
    firebaseConfigured: boolean;
    logout(): void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
