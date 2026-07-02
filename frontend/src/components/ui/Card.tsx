interface Props {

    title: string;

    subtitle?: string;

    action?: React.ReactNode;

    children: React.ReactNode;

}

export default function Card({

    title,

    subtitle,

    action,

    children,

}: Props) {

    return (

        <div

            className="

                rounded-2xl

                border

                border-slate-800

                bg-slate-900

                p-6

                shadow-lg

            "

        >

            <div className="flex justify-between items-start mb-6">

                <div>

                    <h2 className="text-xl font-semibold">

                        {title}

                    </h2>

                    {

                        subtitle && (

                            <p className="text-slate-400 mt-1">

                                {subtitle}

                            </p>

                        )

                    }

                </div>

                {action}

            </div>

            {children}

        </div>

    );

}