import { useState } from "react";

import HistoryStatistics from "../components/HistoryStatistics";
import HistoryToolbar from "../components/HistoryToolbar";
import HistoryTable from "../components/HistoryTable";
import HistoryPagination from "../components/HistoryPagination";
import HistoryDetailModal from "../components/HistoryDetailModal";
import DeleteDialog from "../components/DeleteDialog";

import EmptyState from "../../../components/ui/EmptyState";
import Spinner from "../../../components/ui/Spinner";

import { useHistory } from "../hooks/useHistory";

import type { HistoryItem } from "../types/history";

export default function HistoryPage() {

    const {

        loading,

        error,

        history,

        totalHistory,

        search,

        setSearch,

        page,

        setPage,

        totalPages,

        loadHistory,

        remove,

        download,

    } = useHistory();

    const [

        selected,

        setSelected,

    ] = useState<HistoryItem | null>(null);

    const [

        detailOpen,

        setDetailOpen,

    ] = useState(false);

    const [

        deleteOpen,

        setDeleteOpen,

    ] = useState(false);

    function handleView(

        item: HistoryItem,

    ) {

        setSelected(item);

        setDetailOpen(true);

    }

    function handleDelete(

        id: number,

    ) {

        const item = totalHistory.find(

            x => x.id === id,

        );

        if (!item) {

            return;

        }

        setSelected(item);

        setDeleteOpen(true);

    }

    async function confirmDelete() {

        if (!selected) {

            return;

        }

        await remove(

            selected.id,

        );

        setDeleteOpen(false);

        setSelected(null);

    }

    return (

        <div className="space-y-8">

            {/* ============================= */}

            {/* Header */}

            {/* ============================= */}

            <div>

                <h1 className="text-3xl font-bold">

                    Detection History

                </h1>

                <p className="text-slate-400 mt-2">

                    Review, manage and download previous AI detections.

                </p>

            </div>

            {/* ============================= */}

            {/* Error */}

            {/* ============================= */}

            {

                error && (

                    <EmptyState

                        title="History Error"

                        description={error}

                    />

                )

            }

            {/* ============================= */}

            {/* Statistics */}

            {/* ============================= */}

            <HistoryStatistics

                history={totalHistory}

            />

            {/* ============================= */}

            {/* Toolbar */}

            {/* ============================= */}

            <HistoryToolbar

                search={search}

                onSearch={setSearch}

                onRefresh={loadHistory}

            />

            {/* ============================= */}

            {/* Loading */}

            {/* ============================= */}

            {

                loading ? (

                    <Spinner />

                )

                :

                (

                    <>

                        <HistoryTable

                            loading={loading}

                            history={history}

                            onView={handleView}

                            onDownload={download}

                            onDelete={handleDelete}

                        />

                        <HistoryPagination

                            page={page}

                            totalPages={totalPages}

                            onPrevious={() =>

                                setPage(

                                    Math.max(

                                        1,

                                        page - 1,

                                    ),

                                )

                            }

                            onNext={() =>

                                setPage(

                                    Math.min(

                                        totalPages,

                                        page + 1,

                                    ),

                                )

                            }

                        />

                    </>

                )

            }

            {/* ============================= */}

            {/* Detail */}

            {/* ============================= */}

            <HistoryDetailModal

                open={detailOpen}

                item={selected}

                onClose={() => {

                    setDetailOpen(false);

                    setSelected(null);

                }}

                onDownload={() => {

                    if (

                        selected

                    ) {

                        download(

                            selected.id,

                        );

                    }

                }}

            />

            {/* ============================= */}

            {/* Delete */}

            {/* ============================= */}

            <DeleteDialog

                open={deleteOpen}

                filename={selected?.filename}

                onCancel={() => {

                    setDeleteOpen(false);

                    setSelected(null);

                }}

                onConfirm={confirmDelete}

            />

        </div>

    );

}