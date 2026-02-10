import Button from '../common/Button'
import Card from '../common/Card'
import { LoginIcon, UserAddIcon, UsersIcon, ShieldCheckIcon } from '../icons/Icons'

const HeroSection = () => {
    return (
        <div className='max-w-4xl w-full text-center space-y-12'>
            {/* Hero Section */}
            <div className='space-y-4'>
                <h1 className='text-6xl font-bold bg-linear-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent'>
                    Infinite Tic Tac Toe
                </h1>
                <p className='text-xl text-gray-300'>
                    A classic game reinvented, no ties allowed.
                </p>
                <p className='text-gray-400 text-lg mt-2'>
                    An incredible gaming experience awaits you.
                </p>
            </div>

            {/* Action Buttons */}
            <div className='flex gap-6 justify-center items-center flex-wrap'>
                <Button variant='hero' icon={<LoginIcon />}>
                    Login
                </Button>
                <Button variant='hero' className='hover:shadow-blue-500/50' icon={<UserAddIcon />}>
                    Register
                </Button>
            </div>

            {/* Feature Cards */}
            <div className='flex gap-6 justify-center items-center flex-wrap pt-8'>
                <Card title='Multiplayer' icon={<UsersIcon />} />
                <Card title='Secure' icon={<ShieldCheckIcon />} />
            </div>
        </div>
    )
}

export default HeroSection
