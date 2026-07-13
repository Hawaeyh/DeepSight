import {

    createContext,

    useContext,

} from "react";

import type { ReactNode } from "react";

import { useDashboard } from "../hooks/useDashboard";

const DashboardContext =

createContext<any>(null);

export function DashboardProvider({

    children,

}:{

    children:ReactNode;

}){

    const dashboard=

    useDashboard();

    return(

        <DashboardContext.Provider

            value={dashboard}

        >

            {children}

        </DashboardContext.Provider>

    );

}

export function useDashboardContext(){

    return useContext(

        DashboardContext

    );

}
