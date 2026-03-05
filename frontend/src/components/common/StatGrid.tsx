import StatCard from './StatCard'

interface StatItem {
    icon: React.ReactNode
    value: string
    label: string
    color?: string
}

interface StatGridProps {
    title?: string
    stats: StatItem[]
    columns?: 2 | 3 | 4
    className?: string
}

const columnClasses = {
    2: 'grid-cols-2',
    3: 'grid-cols-2 sm:grid-cols-3',
    4: 'grid-cols-2 sm:grid-cols-4',
}

const StatGrid = ({
    title,
    stats,
    columns = 4,
    className = '',
}: StatGridProps) => {
    return (
        <div className={`space-y-3 ${className}`}>
            {title && (
                <h3 className='profile-section-title'>
                    {title}
                </h3>
            )}

            <div className={`grid ${columnClasses[columns]} gap-3`}>
                {stats.map((stat, index) => (
                    <StatCard
                        key={`${stat.label}-${index}`}
                        icon={stat.icon}
                        value={stat.value}
                        label={stat.label}
                        color={stat.color}
                    />
                ))}
            </div>
        </div>
    )
}

export default StatGrid
