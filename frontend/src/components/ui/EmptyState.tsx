interface Props {

    title: string;

    description: string;

}

export default function EmptyState({

    title,

    description,

}: Props) {

    return (

        <div className="py-20 text-center">

            <h2 className="text-2xl font-semibold">

                {title}

            </h2>

            <p className="mt-3 text-slate-400">

                {description}

            </p>

        </div>

    );

}