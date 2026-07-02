interface Props {

    loading: boolean;

    disabled: boolean;

    onAnalyze(): void;

    onReset(): void;

}

export default function ActionButtons({

    loading,

    disabled,

    onAnalyze,

    onReset,

}: Props) {

    return (

        <div className="flex gap-4">

            <button

                onClick={onAnalyze}

                disabled={disabled || loading}

                className="flex-1 rounded-xl bg-cyan-500 hover:bg-cyan-600 disabled:bg-slate-700 py-3 font-semibold transition"

            >

                {

                    loading

                        ? "Analyzing..."

                        : "Analyze Image"

                }

            </button>

            <button

                onClick={onReset}

                className="rounded-xl border border-slate-700 px-6 hover:bg-slate-800 transition"

            >

                Reset

            </button>

        </div>

    );

}