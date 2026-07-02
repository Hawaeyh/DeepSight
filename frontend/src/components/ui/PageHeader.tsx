interface Props {

    title: string;

    description: string;

}

export default function PageHeader({

    title,

    description,

}: Props) {

    return (

        <div className="mb-8">

            <h1 className="text-4xl font-bold tracking-tight">

                {title}

            </h1>

            <p className="text-slate-400 mt-2">

                {description}

            </p>

        </div>

    );

}