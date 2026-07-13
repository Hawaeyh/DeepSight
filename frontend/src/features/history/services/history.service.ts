import api from "../../../services/api";

import type {

    HistoryItem,

} from "../types/history";

export async function getHistory(): Promise<HistoryItem[]> {

    const { data } = await api.get(

        "/history",

    );

    return data;

}

export async function getHistoryById(

    id: number,

): Promise<HistoryItem> {

    const { data } = await api.get(

        `/history/${id}`,

    );

    return data;

}

export async function deleteHistory(

    id: number,

): Promise<void> {

    await api.delete(

        `/history/${id}`,

    );

}

export async function downloadHistoryReport(

    id: number,

): Promise<Blob> {

    const { data } = await api.get(

        `/reports/${id}`,

        {

            responseType: "blob",

        },

    );

    return data;

}