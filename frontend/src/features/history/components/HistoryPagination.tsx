import Button from "../../../components/ui/Button";

interface Props {

    page: number;

    totalPages: number;

    onPrevious: () => void;

    onNext: () => void;

}

export default function HistoryPagination({

    page,

    totalPages,

    onPrevious,

    onNext,

}: Props) {

    return (

        <div

            className="

                flex

                items-center

                justify-between

                mt-8

            "

        >

            <Button

                disabled={page <= 1}

                onClick={onPrevious}

                className="bg-slate-700 hover:bg-slate-600"

            >

                Previous

            </Button>

            <div className="text-slate-400">

                Page

                <span className="mx-2 font-bold text-white">

                    {page}

                </span>

                of

                <span className="mx-2 font-bold text-white">

                    {totalPages}

                </span>

            </div>

            <Button

                disabled={page >= totalPages}

                onClick={onNext}

                className="bg-slate-700 hover:bg-slate-600"

            >

                Next

            </Button>

        </div>

    );

}