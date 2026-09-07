import type { AxiosRequestConfig } from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";

import api, { resetUnauthorizedState, setUnauthorizedHandler } from "./api";

describe("authenticated API client", () => {
    beforeEach(() => {
        localStorage.clear();
        resetUnauthorizedState();
        setUnauthorizedHandler(null);
    });

    it("adds the bearer token to authenticated requests", async () => {
        localStorage.setItem("deepsight-access-token", "local-jwt");
        let received: AxiosRequestConfig | undefined;
        const original = api.defaults.adapter;
        api.defaults.adapter = async config => { received = config; return { data: {}, status: 200, statusText: "OK", headers: {}, config }; };
        try { await api.get("/dashboard/overview"); } finally { api.defaults.adapter = original; }
        expect(received?.headers?.Authorization).toBe("Bearer local-jwt");
    });

    it("handles concurrent 401 responses once without retrying", async () => {
        localStorage.setItem("deepsight-access-token", "expired");
        const handler = vi.fn();
        const adapter = vi.fn(async config => Promise.reject({ config, response: { status: 401, data: {} }, message: "Unauthorized" }));
        const original = api.defaults.adapter;
        setUnauthorizedHandler(handler);
        api.defaults.adapter = adapter;
        try { await Promise.allSettled([api.get("/history"), api.get("/dashboard/overview")]); } finally { api.defaults.adapter = original; }
        expect(handler).toHaveBeenCalledTimes(1);
        expect(adapter).toHaveBeenCalledTimes(2);
        expect(localStorage.getItem("deepsight-access-token")).toBeNull();
    });
});
