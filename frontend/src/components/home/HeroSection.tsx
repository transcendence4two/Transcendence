import Button from '../common/Button'
import Card from '../common/Card'
import { LoginIcon, UserAddIcon, UsersIcon, ShieldCheckIcon } from '../icons/Icons'

const HeroSection = () => {
    return (
        <div className='max-w-4xl w-full text-center space-y-6 sm:space-y-12'>
            {/* Hero Section */}
            <div className='space-y-4'>
                <h1 className='text-4xl sm:text-6xl font-bold bg-linear-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent'>
                    Tic Tac Infinity
                </h1>
                <p className='text-lg sm:text-xl text-gray-300'>
                    A classic game reinvented, no ties allowed.
                </p>
                <p className='text-gray-400 text-base sm:text-lg mt-2'>
                    An incredible gaming experience awaits you.
                </p>
            </div>

            {/* Action Buttons */}
            <div className='flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center'>
                <Button
                    variant='hero'
                    className='hover:shadow-blue-500/50'
                    icon={<LoginIcon />}
                    onClick={() => window.location.href = '/login'}
                >
                    Login
                </Button>
                <Button
                    variant='hero'
                    className='hover:shadow-blue-500/50'
                    icon={<UserAddIcon />}
                    onClick={() => window.location.href = '/register'}
                >
                    Register
                </Button>
            </div>

            {/* Feature Cards */}
            <div className='flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center'>
                <Card title='Multiplayer' icon={<UsersIcon />} />
                <Card title='Secure' icon={<ShieldCheckIcon />} />
            </div>
        </div>
    )
}

export default HeroSection
