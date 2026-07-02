interface Props {

    text: string;

    color?: "green" | "red" | "yellow" | "cyan";

}

export default function Badge({

    text,

    color = "cyan",

}: Props) {

    const colors = {

        green: "bg-green-500",

        red: "bg-red-500",

        yellow: "bg-yellow-500",

        cyan: "bg-cyan-500",

    };

    return (

        <span
            className={`
                rounded-full
                px-3
                py-1
                text-sm
                font-semibold
                text-white
                ${colors[color]}
            `}
        >

            {text}

        </span>

    );

}