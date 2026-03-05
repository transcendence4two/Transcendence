import { cloneElement, isValidElement, type ReactNode } from "react";

interface StatCardProps {
    icon: ReactNode
    value: string
    label: string
    color?: string
    className?: string
}

const resolveIconColorClass = (color: string) => {
    if (color.includes("emerald")) return "icon-emerald"
    if (color.includes("rose") || color.includes("red")) return "icon-rose"
    if (color.includes("blue")) return "icon-blue"
    return "icon-cyan"
}

const StatCard = ({
    icon,
    value,
    label,
    color = 'text-cyan-400',
    className = '',
}: StatCardProps) => {
    const iconColorClass = resolveIconColorClass(color)
    const styledIcon = isValidElement<{ className?: string }>(icon)
        ? cloneElement(icon, {
              className: `${icon.props.className ?? ""} stat-icon icon-svg ${iconColorClass}`.trim(),
          })
        : icon

    return (
        <div
            className={`stat-card ${className}`}
        >
            {styledIcon}
            <p className='stat-value text-white'>{value}</p>
            <p className='stat-label'>{label}</p>
        </div>
    )
}

export default StatCard
