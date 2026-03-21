import { useState, useEffect } from 'react'
import { SunIcon, MoonIcon, GitHubIcon } from '../icons/Icons'
import HamburgerMenu from '../common/HamburgerMenu'

const Header = () => {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const savedTheme = localStorage.getItem('theme')
        return savedTheme ? savedTheme === 'dark' : true
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
        <header className='header-main relative flex items-center'>
            <HamburgerMenu />

            <div className='ml-auto flex items-center gap-1'>
                <a
                    href='https://github.com/transcendence4two/Transcendence'
                    target='_blank'
                    rel='noopener noreferrer'
                    className='p-2 rounded-lg hover:bg-gray-700/50 in-[.light]:hover:bg-gray-200 transition-colors text-white in-[.light]:text-gray-700'
                    aria-label='GitHub repository'
                >
                    <GitHubIcon />
                </a>
                <button
                    onClick={toggleTheme}
                    className='p-2 rounded-lg hover:bg-gray-700/50 in-[.light]:hover:bg-gray-200 transition-colors z-10'
                    aria-label='Toggle theme'
                >
                    {isDarkMode ? <SunIcon /> : <MoonIcon />}
                </button>
            </div>
        </header>
    )
}

export default Header
