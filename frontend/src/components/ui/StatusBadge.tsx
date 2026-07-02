interface Props {

    text: string;

    color?:

        | "green"

        | "red"

        | "yellow"

        | "blue"

        | "gray";

}

export default function StatusBadge({

    text,

    color = "blue",

}: Props) {

    const styles = {

        green:

            "bg-green-500/15 text-green-400",

        red:

            "bg-red-500/15 text-red-400",

        yellow:

            "bg-yellow-500/15 text-yellow-400",

        blue:

            "bg-cyan-500/15 text-cyan-400",

        gray:

            "bg-slate-500/15 text-slate-300",

    };

    return (

        <span

            className={`

                px-3

                py-1

                rounded-full

                text-xs

                font-semibold

                ${styles[color]}

            `}

        >

            {text}

        </span>

    );

}