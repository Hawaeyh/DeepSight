import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import App from "./App";


describe("application routing", () => {
    beforeEach(() => {
        localStorage.clear();
        window.history.replaceState({}, "", "/");
    });

    it("renders the public home route", async () => {
        render(<App />);
        expect(await screen.findByRole("heading", { level: 1, name: "DeepSight System" })).toBeInTheDocument();
    });

    it("redirects an unknown route without crashing", async () => {
        window.history.replaceState({}, "", "/does-not-exist");
        render(<App />);
        expect(await screen.findByRole("heading", { level: 1, name: "DeepSight System" })).toBeInTheDocument();
        expect(window.location.pathname).toBe("/");
    });
});
