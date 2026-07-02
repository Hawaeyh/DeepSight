interface Props {

    title: string;

    subtitle?: string;

}

export default function SectionTitle({

    title,

    subtitle,

}: Props) {

    return (

        <div>

            <h1 className="text-3xl font-bold">

                {title}

            </h1>

            {

                subtitle && (

                    <p className="mt-2 text-slate-400">

                        {subtitle}

                    </p>

                )

            }

        </div>

    );

}