import type { ReactNode } from "react";

import { useDashboard } from "../hooks/useDashboard";
import { DashboardContext } from "./dashboard-context";


export function DashboardProvider({ children }: { children: ReactNode }) {
    const dashboard = useDashboard();
    return <DashboardContext.Provider value={dashboard}>{children}</DashboardContext.Provider>;
}
