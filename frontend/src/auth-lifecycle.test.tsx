import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiGet, apiPost } = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn() }));

vi.mock("./services/api", () => ({
    default: { get: apiGet, post: apiPost },
    ensureGuestSession: vi.fn(() => Promise.resolve()),
    resetUnauthorizedState: vi.fn(),
    setUnauthorizedHandler: vi.fn(),
}));

import App from "./App";

const user = { id: 1, full_name: "Test User", email: "test@example.com", role: "user", plan: "starter" };
const protectedPaths = ["/history", "/dashboard/overview", "/dashboard/trend", "/dashboard/distribution", "/dashboard/recent", "/dashboard/models"];

describe("authenticated request lifecycle", () => {
    beforeEach(() => {
        localStorage.clear();
        apiGet.mockReset();
        apiPost.mockReset();
        apiGet.mockResolvedValue({ data: { authenticated: false, plan: { key: "starter", name: "Starter", price: "Free", limit: 2, windowHours: 24, features: [] }, used: 0, remaining: 2, resetsAt: null } });
        window.history.replaceState({}, "", "/");
    });

    it("does not request dashboard data from the logged-out homepage", async () => {
        render(<App />);
        await screen.findByRole("heading", { level: 1, name: "DeepSight System" });
        expect(apiGet.mock.calls.some(([path]) => protectedPaths.includes(path))).toBe(false);
    });

    it("allows logged-out pricing without requesting private data", async () => {
        window.history.replaceState({}, "", "/plans");
        apiGet.mockImplementation((path: string) => Promise.resolve({ data: path.endsWith("/plans") ? [] : { authenticated: false, plan: { key: "starter", name: "Starter", price: "Free", limit: 2, windowHours: 24, features: [] }, used: 0, remaining: 2, resetsAt: null } }));
        render(<App />);
        await screen.findByRole("heading", { name: "Subscription Plans" });
        expect(apiGet.mock.calls.some(([path]) => protectedPaths.includes(path))).toBe(false);
    });

    it("waits for restoration before mounting a protected dashboard", async () => {
        localStorage.setItem("deepsight-access-token", "token");
        window.history.replaceState({}, "", "/dashboard");
        let resolveRestore!: (value: { data: typeof user }) => void;
        apiGet.mockImplementation((path: string) => path === "/auth/me" ? new Promise(resolve => { resolveRestore = resolve; }) : Promise.resolve({ data: emptyDashboard(path) }));
        render(<App />);
        expect(screen.queryByText("Welcome, Test")).not.toBeInTheDocument();
        expect(apiGet.mock.calls.filter(([path]) => path === "/auth/me")).toHaveLength(1);
        resolveRestore({ data: user });
        await screen.findByText("Welcome, Test");
        await waitFor(() => protectedPaths.slice(1).forEach(path => expect(apiGet.mock.calls.filter(([called]) => called === path)).toHaveLength(1)));
    });

    it("redirects a logged-out protected route to login", async () => {
        window.history.replaceState({}, "", "/history");
        render(<App />);
        await screen.findByRole("heading", { name: "DeepSight System" });
        await waitFor(() => expect(window.location.pathname).toBe("/login"));
        expect(apiGet.mock.calls.some(([path]) => protectedPaths.includes(path))).toBe(false);
    });
});

function emptyDashboard(path: string) {
    if (path === "/dashboard/overview") return { totalDetection: 0, todayDetection: 0 };
    if (path === "/dashboard/distribution") return { real: 0, fake: 0 };
    if (path === "/subscriptions/status") return { authenticated: true, plan: { name: "Starter" }, remaining: 2 };
    return [];
}
