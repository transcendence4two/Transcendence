import { useState } from 'react'
import { SunIcon, MoonIcon } from '../icons/Icons'

const Header = () => {
    const [isDarkMode, setIsDarkMode] = useState(true)

    const toggleTheme = () => {
        setIsDarkMode(!isDarkMode)
        document.documentElement.classList.toggle('light')
    }

    return (
        <header className='header-main relative'>
            <button
                onClick={toggleTheme}
                className='absolute top-4 right-4 p-2 rounded-lg hover:bg-gray-700/50 transition-colors z-10'
                aria-label='Toggle theme'
            >
                {isDarkMode ? <SunIcon /> : <MoonIcon />}
            </button>
        </header>
    )
}

export default Header
