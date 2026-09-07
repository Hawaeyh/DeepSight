import { useContext } from "react";

import { DashboardContext } from "../context/dashboard-context";


export function useDashboardContext() {
    return useContext(DashboardContext);
}
