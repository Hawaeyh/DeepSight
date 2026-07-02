import Button from "../../../components/ui/Button";

interface Props {

    loading: boolean;

    disabled: boolean;

    canDownload: boolean;

    onAnalyze(): void;

    onDownload(): void;

    onReset(): void;

    onHistory(): void;

}

export default function ActionBar({

    loading,

    disabled,

    canDownload,

    onAnalyze,

    onDownload,

    onReset,

    onHistory,

}: Props) {

    return (

        <div
            className="
                rounded-2xl
                border
                border-slate-800
                bg-slate-900
                p-6
            "
        >

            <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">

                <Button

                    onClick={onAnalyze}

                    disabled={disabled || loading}

                >

                    {

                        loading

                            ? "Analyzing..."

                            : "Analyze Image"

                    }

                </Button>

                <Button

                    variant="secondary"

                    onClick={onDownload}

                    disabled={!canDownload}

                >

                    Download Report

                </Button>

                <Button

                    variant="secondary"

                    onClick={onHistory}

                >

                    View History

                </Button>

                <Button

                    variant="danger"

                    onClick={onReset}

                >

                    Reset

                </Button>

            </div>

        </div>

    );

}