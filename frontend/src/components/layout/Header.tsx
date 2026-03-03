import { useState, useEffect } from 'react'
import { SunIcon, MoonIcon } from '../icons/Icons'
import HamburgerMenu from '../common/HamburgerMenu'

const Header = () => {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const savedTheme = localStorage.getItem('theme')
        return savedTheme ? savedTheme === 'dark' : true
    })

    const [isLoggedIn] = useState(() => {
        return !!localStorage.getItem('access_token')
    })

    useEffect(() => {
        const root = document.documentElement
        if (isDarkMode) {
            root.classList.remove('light')
            localStorage.setItem('theme', 'dark')
        } else {
            root.classList.add('light')
            localStorage.setItem('theme', 'light')
        }
    }, [isDarkMode])

    const toggleTheme = () => {
        setIsDarkMode(prev => !prev)
    }

    return (
        <header className='header-main relative flex items-center justify-between'>
            <div className='flex items-center'>
                {isLoggedIn && <HamburgerMenu />}
            </div>

            <div className='flex items-center'>
                <button
                    onClick={toggleTheme}
                    className='p-2 rounded-lg hover:bg-gray-700/50 transition-colors z-10'
                    aria-label='Toggle theme'
                >
                    {isDarkMode ? <SunIcon /> : <MoonIcon />}
                </button>
            </div>
        </header>
    )
}

export default Header
