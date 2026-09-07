import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

import { useAuth } from "../hooks/useAuth";
import { AuthProvider } from "./AuthContext";

const mocks = vi.hoisted(() => ({
    get: vi.fn(),
    post: vi.fn(),
    restoredFirebaseUser: vi.fn(),
    observeFirebaseToken: vi.fn(() => () => undefined),
}));

vi.mock("../services/api", () => ({
    default: { get: mocks.get, post: mocks.post },
    ensureGuestSession: vi.fn(() => Promise.resolve()),
    resetUnauthorizedState: vi.fn(),
    setUnauthorizedHandler: vi.fn(),
}));

vi.mock("../services/firebaseAuth", () => ({
    firebaseConfigured: true,
    firebaseEmailLogin: vi.fn(),
    firebaseEmailRegister: vi.fn(),
    firebaseGoogleLogin: vi.fn(),
    firebaseLogout: vi.fn(),
    restoredFirebaseUser: mocks.restoredFirebaseUser,
    observeFirebaseToken: mocks.observeFirebaseToken,
}));

function AuthConsumer() {
    const { loading, authStatus, user } = useAuth();
    return <div>{loading ? "Loading account" : `${authStatus}:${user?.email ?? "guest"}`}</div>;
}

beforeEach(() => {
    localStorage.clear();
    mocks.get.mockReset();
    mocks.post.mockReset();
    mocks.restoredFirebaseUser.mockReset();
    mocks.restoredFirebaseUser.mockResolvedValue(null);
});

it("exposes loading while restoring a stored DeepSight session", () => {
    localStorage.setItem("deepsight-access-token", "test-token");
    mocks.get.mockReturnValue(new Promise(() => undefined));
    render(<AuthProvider><AuthConsumer /></AuthProvider>);
    expect(screen.getByText("Loading account")).toBeInTheDocument();
});

it("restores a Firebase identity and exchanges its ID token for a local session", async () => {
    const getIdToken = vi.fn().mockResolvedValue("realistic-firebase-id-token");
    mocks.restoredFirebaseUser.mockResolvedValue({ getIdToken });
    mocks.post.mockResolvedValue({ data: { access_token: "local-jwt", token_type: "bearer", user: { id: 9, email: "firebase@example.com", full_name: "Firebase User", role: "user", plan: "starter" } } });
    render(<AuthProvider><AuthConsumer /></AuthProvider>);
    await waitFor(() => expect(screen.getByText("authenticated:firebase@example.com")).toBeInTheDocument());
    expect(getIdToken).toHaveBeenCalledOnce();
    expect(mocks.post).toHaveBeenCalledWith("/auth/firebase", { id_token: "realistic-firebase-id-token" });
    expect(localStorage.getItem("deepsight-access-token")).toBe("local-jwt");
});
