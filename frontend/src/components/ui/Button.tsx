import type { ButtonHTMLAttributes, ReactNode } from "react";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
    children: ReactNode;
    variant?: "primary" | "secondary" | "danger";
}

const variantClasses = {
    primary: "bg-cyan-500 hover:bg-cyan-400",
    secondary: "bg-slate-700 hover:bg-slate-600",
    danger: "bg-red-600 hover:bg-red-500",
};

export default function Button({
    children,
    className = "",
    variant = "primary",
    ...props
}: Props) {
    return (
        <button
            {...props}
            className={`rounded-xl px-6 py-3 font-semibold transition disabled:opacity-50 ${variantClasses[variant]} ${className}`}
        >
            {children}
        </button>
    );
}
