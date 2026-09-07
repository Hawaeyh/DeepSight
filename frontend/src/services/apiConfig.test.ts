import { describe, expect, it } from "vitest";

import { getApiBaseUrl } from "./apiConfig";


describe("API base URL configuration", () => {
    it("uses an explicit configured URL", () => {
        expect(getApiBaseUrl("https://api.example.test/api/v1")).toBe("https://api.example.test/api/v1");
    });

    it("uses the local URL when configuration is blank", () => {
        expect(getApiBaseUrl("   ")).toBe("http://127.0.0.1:8000/api/v1");
    });
});
