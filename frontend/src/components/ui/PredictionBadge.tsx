interface Props{

    prediction:string;

}

export default function PredictionBadge({

    prediction,

}:Props){

    const real=

        prediction==="Real";

    return(

        <span

            className={`

            px-5

            py-2

            rounded-full

            font-semibold

            ${

                real

                ?

                "bg-green-500/20 text-green-400"

                :

                "bg-red-500/20 text-red-400"

            }

            `}

        >

            {prediction}

        </span>

    );

}