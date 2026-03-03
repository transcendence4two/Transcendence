interface StatCardProps {
    icon: React.ReactNode
    value: string
    label: string
    color?: string
    className?: string
}

const StatCard = ({
    icon,
    value,
    label,
    color = 'text-cyan-400',
    className = '',
}: StatCardProps) => {
    return (
        <div
            className={`border border-slate-700/50 in-[.light]:border-gray-200
                bg-slate-800/50 in-[.light]:bg-white/80
                backdrop-blur-sm rounded-xl p-4 text-center space-y-1 ${className}`}
        >
            <span className='flex justify-center text-slate-400 in-[.light]:text-gray-500'>{icon}</span>
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className='text-xs text-slate-400 in-[.light]:text-gray-500'>{label}</p>
        </div>
    )
}

export default StatCard
