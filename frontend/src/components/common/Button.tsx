interface ButtonProps {
    children: React.ReactNode
    onClick?: () => void
    variant?: 'primary' | 'secondary' | 'hero'
    icon?: React.ReactNode
    className?: string
    disabled?: boolean
}

const Button = ({ children, onClick, variant = 'primary', icon, className = '', disabled }: ButtonProps) => {
    const variantClasses = {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        hero: 'btn-hero'
    }

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`${variantClasses[variant]} ${className}`}
        >
            {icon && <span className='flex items-center'>{icon}</span>}
            {children}
        </button>
    )
}

export default Button
