interface Props {

    value: number;

}

export default function ProgressBar({

    value,

}: Props) {

    return (

        <div className="h-3 rounded-full bg-slate-800">

            <div

                className="h-full rounded-full bg-cyan-500"

                style={{

                    width: `${value}%`,

                }}

            />

        </div>

    );

}