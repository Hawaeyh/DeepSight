import {

    useCallback,

    useEffect,

    useMemo,

    useState,

} from "react";

import {

    deleteHistory,

    downloadHistoryReport,

    getHistory,

} from "../services/history.service";

import {

    downloadFile,

} from "../../image/utils/downloadFile";

import type {

    HistoryItem,

} from "../types/history";

export function useHistory() {

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

    ] = useState("");

    const [

        page,

        setPage,

    ] = useState(1);

    const pageSize = 8;

    const loadHistory = useCallback(async () => {

        try {

            setLoading(true);

            setError(null);

            const response = await getHistory();

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

    }, []);

    useEffect(() => {

        loadHistory();

    }, [loadHistory]);

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

    };

}