import type { ButtonHTMLAttributes } from "react";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {

    children: React.ReactNode;

}

export default function Button({

    children,

    className = "",

    ...props

}: Props) {

    return (

        <button

            {...props}

            className={`
                rounded-xl
                bg-cyan-500
                px-6
                py-3
                font-semibold
                transition
                hover:bg-cyan-400
                disabled:opacity-50
                ${className}
            `}

        >

            {children}

        </button>

    );

}