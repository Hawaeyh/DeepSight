export interface AdminUser {
    id: number;
    fullName: string;
    email: string;
    role: "user" | "admin";
    plan: "starter" | "basic" | "lite";
    isActive: boolean;
    usageCount: number;
    lastUsedAt: string | null;
    createdAt: string;
}

export interface UserUsagePoint {
    date: string;
    runs: number;
    activeUsers: number;
}

export interface AdminUsageAnalytics {
    totalUsers: number;
    activeUsers: number;
    totalRuns: number;
    runsLast14Days: number;
    trend: UserUsagePoint[];
    plans: Array<{ plan: string; users: number }>;
}

export interface AdminSystemOverview {
    totalUsers: number; activeUsers: number; newUsersToday: number; totalAnalyses: number; analysesToday: number;
    failedAnalyses: number; activeSubscriptions: number; videoQueue: number; activeVideoJobs: number; failedVideoJobs: number;
    averageProcessingTime: number | null;
}
