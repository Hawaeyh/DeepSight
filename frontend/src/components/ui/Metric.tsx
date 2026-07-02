interface Props {

    label: string;

    value: string | number;

}

export default function Metric({

    label,

    value,

}: Props) {

    return (

        <div className="flex justify-between items-center">

            <span className="text-slate-400">

                {label}

            </span>

            <span className="font-medium">

                {value}

            </span>

        </div>

    );

}