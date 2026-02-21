interface ButtonProps {
    children: React.ReactNode
    onClick?: () => void
    variant?: 'primary' | 'secondary' | 'hero'
    icon?: React.ReactNode
    className?: string
    disabled?: boolean
    type?: 'button' | 'submit' | 'reset'
}

const Button = ({
    children,
    onClick,
    variant = 'primary',
    icon,
    className = '',
    disabled,
    type = 'button'
}: ButtonProps) => {
    const variantClasses = {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        hero: 'btn-hero'
    }

    return (
        <button
            type={type}
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
