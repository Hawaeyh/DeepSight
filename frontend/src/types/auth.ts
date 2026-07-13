export interface AuthUser {
    id: number;
    full_name: string;
    email: string;
    role: string;
    plan: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: AuthUser;
}

export interface Plan {
    key: "starter" | "basic" | "lite";
    name: string;
    price: string;
    limit: number | null;
    windowHours: number | null;
    features: string[];
}

export interface UsageStatus {
    authenticated: boolean;
    plan: Plan;
    used: number;
    remaining: number | null;
    resetsAt: string | null;
}
