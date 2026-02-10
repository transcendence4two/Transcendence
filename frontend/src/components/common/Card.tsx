interface CardProps {
    icon: React.ReactNode
    title: string
    className?: string
}

const Card = ({ icon, title, className = '' }: CardProps) => {
    return (
        <div className={`card-feature ${className}`}>
            <div className='w-16 h-16 mx-auto mb-4 text-cyan-400'>
                {icon}
            </div>
            <p className='text-gray-300 text-lg font-medium'>{title}</p>
        </div>
    )
}

export default Card
