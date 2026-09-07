import {

    useCallback,

    useEffect,

    useMemo,

    useRef,

    useState,

} from "react";

import {

    deleteHistory,

    downloadHistoryReport,

    getHistory,
    verifyHistory,

} from "../services/history.service";

import {

    downloadFile,

} from "../../image/utils/downloadFile";

import type {

    HistoryItem,

} from "../types/history";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "../../../hooks/useAuth";

export function useHistory() {

    const { authStatus } = useAuth();
    const authStatusRef = useRef(authStatus);
    authStatusRef.current = authStatus;

    const [searchParams] = useSearchParams();

    const [

        history,

        setHistory,

    ] = useState<HistoryItem[]>([]);

    const [

        loading,

        setLoading,

    ] = useState(true);

    const [

        error,

        setError,

    ] = useState<string | null>(null);

    const [

        search,

        setSearch,

    ] = useState(searchParams.get("search") ?? "");

    const [

        page,

        setPage,

    ] = useState(1);

    const pageSize = 8;

    const loadHistory = useCallback(async () => {

        if (authStatus !== "authenticated") {
            setHistory([]);
            setLoading(authStatus === "loading");
            return;
        }

        try {

            setLoading(true);

            setError(null);

            const response = await getHistory();

            if (authStatusRef.current !== "authenticated") return;

            setHistory(response);

        }

        catch {

            setError(

                "Unable to load history.",

            );

        }

        finally {

            setLoading(false);

        }

    }, [authStatus]);

    useEffect(() => {

        if (authStatus === "authenticated") loadHistory();
        else { setHistory([]); setLoading(authStatus === "loading"); setError(null); }

    }, [authStatus, loadHistory]);

    async function remove(id: number) {

        await deleteHistory(id);

        await loadHistory();

    }

    async function download(id: number) {

        const pdf = await downloadHistoryReport(id);

        downloadFile(

            pdf,

            `Analysis_${id}.pdf`,

        );

    }

    async function verify(id: number, verifiedResult: "Real" | "Fake") {
        const updated = await verifyHistory(id, verifiedResult);
        await loadHistory();
        return updated;
    }

    const filtered = useMemo(() => {

        return history.filter(item =>

            item.filename

                .toLowerCase()

                .includes(

                    search.toLowerCase(),

                ),

        );

    }, [

        history,

        search,

    ]);

    const totalPages = Math.max(

        1,

        Math.ceil(

            filtered.length / pageSize,

        ),

    );

    const paginated = useMemo(() => {

        const start =

            (page - 1) * pageSize;

        return filtered.slice(

            start,

            start + pageSize,

        );

    }, [

        filtered,

        page,

    ]);

    return {

        loading,

        error,

        search,

        setSearch,

        page,

        setPage,

        totalPages,

        history: paginated,

        totalHistory: filtered,

        loadHistory,

        remove,

        download,

        verify,

    };

}
