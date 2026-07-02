import type { InputHTMLAttributes } from "react";

export default function Input(

    props: InputHTMLAttributes<HTMLInputElement>

) {

    return (

        <input

            {...props}

            className="
                w-full
                rounded-xl
                border
                border-slate-700
                bg-slate-900
                px-4
                py-3
                outline-none
                focus:border-cyan-500
            "

        />

    );

}