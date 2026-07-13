import type { ReactNode } from "react";

interface Props {
    title?: string;
    subtitle?: string;
    action?: ReactNode;
    children: ReactNode;
    className?: string;
}

export default function Card({
    title,
    subtitle,
    action,
    children,
    className = "",
}: Props) {
    const hasHeader = title || subtitle || action;

    return (
        <div
            className={`rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg ${className}`}
        >
            {hasHeader && (
                <div className="mb-6 flex items-start justify-between">
                    <div>
                        {title && <h2 className="text-xl font-semibold">{title}</h2>}
                        {subtitle && <p className="mt-1 text-slate-400">{subtitle}</p>}
                    </div>
                    {action}
                </div>
            )}
            {children}
        </div>
    );
}
