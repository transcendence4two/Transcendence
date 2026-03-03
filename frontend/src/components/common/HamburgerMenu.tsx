import { useState, useRef, useEffect } from 'react'
import { HomeIcon, UserIcon, UsersIcon, CogIcon, LogoutIcon } from '../icons/Icons'

interface MenuItem {
    label: string
    icon: React.ReactNode
    href?: string
    onClick?: () => void
    danger?: boolean
    authRequired?: boolean
}

const PUBLIC_PATHS = ['/', '/register', '/login']

const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('temp_token')
    localStorage.removeItem('user')
    window.location.href = '/'
}

const menuItems: MenuItem[] = [
    { label: 'Home', href: '/', icon: <HomeIcon className='w-5 h-5' />, authRequired: false },
    { label: 'Profile', href: '/profile', icon: <UserIcon className='w-5 h-5' />, authRequired: true },
    { label: 'Friends', href: '/friends', icon: <UsersIcon className='w-5 h-5' />, authRequired: true },
    { label: 'Settings', href: '/settings', icon: <CogIcon className='w-5 h-5' />, authRequired: true },
    { label: 'Logout', onClick: handleLogout, icon: <LogoutIcon className='w-5 h-5' />, danger: true, authRequired: true },
]

const HamburgerMenu = () => {
    const [isOpen, setIsOpen] = useState(false)
    const [isLoggedIn] = useState(() => !!localStorage.getItem('access_token'))
    const menuRef = useRef<HTMLDivElement>(null)

    const isPublicPage = PUBLIC_PATHS.includes(window.location.pathname)

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    useEffect(() => {
        const handleEscape = (event: KeyboardEvent) => {
            if (event.key === 'Escape') setIsOpen(false)
        }

        document.addEventListener('keydown', handleEscape)
        return () => document.removeEventListener('keydown', handleEscape)
    }, [])

    if (isPublicPage) return null

    const visibleItems = menuItems.filter(item => !item.authRequired || isLoggedIn)

    return (
        <div ref={menuRef} className='relative'>
            <button
                onClick={() => setIsOpen(prev => !prev)}
                className='p-2 rounded-lg hover:bg-gray-700/50 in-[.light]:hover:bg-gray-200 transition-colors z-10'
                aria-label='Toggle menu'
                aria-expanded={isOpen}
            >
                <svg className='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    {isOpen ? (
                        <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M6 18L18 6M6 6l12 12' />
                    ) : (
                        <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M4 6h16M4 12h16M4 18h16' />
                    )}
                </svg>
            </button>

            {isOpen && (
                <nav
                    className='absolute top-full left-0 mt-2 w-48 bg-slate-800 in-[.light]:bg-white
                        border border-slate-700/50 in-[.light]:border-gray-200
                        rounded-xl shadow-xl in-[.light]:shadow-lg
                        backdrop-blur-sm overflow-hidden z-50'
                >
                    <ul>
                        {visibleItems.map((item, index) => (
                            <li key={item.label}>
                                {item.danger && index > 0 && (
                                    <hr className='border-slate-700/50 in-[.light]:border-gray-200 mx-3' />
                                )}
                                {item.href ? (
                                    <a
                                        href={item.href}
                                        className='flex items-center gap-3 px-4 py-3 text-sm text-slate-300 in-[.light]:text-gray-700
                                            hover:bg-slate-700/50 in-[.light]:hover:bg-gray-100
                                            hover:text-cyan-400 in-[.light]:hover:text-cyan-600
                                            transition-colors'
                                        onClick={() => setIsOpen(false)}
                                    >
                                        {item.icon}
                                        {item.label}
                                    </a>
                                ) : (
                                    <button
                                        className={`w-full flex items-center gap-3 px-4 py-3 text-sm transition-colors
                                            ${item.danger
                                                ? 'text-red-400 hover:bg-red-500/10 hover:text-red-300'
                                                : 'text-slate-300 in-[.light]:text-gray-700 hover:bg-slate-700/50 in-[.light]:hover:bg-gray-100 hover:text-cyan-400'
                                            }`}
                                        onClick={() => { item.onClick?.(); setIsOpen(false) }}
                                    >
                                        {item.icon}
                                        {item.label}
                                    </button>
                                )}
                            </li>
                        ))}
                    </ul>
                </nav>
            )}
        </div>
    )
}

export default HamburgerMenu
