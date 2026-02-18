import Button from '../common/Button'
import { GoogleIcon } from '../icons/Icons'
import { useState } from 'react'

const inputClassName =
    'w-full px-4 py-3 bg-slate-900/50 in-[.light]:bg-gray-100 in-[.light]:border-gray-300 in-[.light]:text-gray-900 border border-slate-600 rounded-xl ' +
    'text-white placeholder-slate-500 in-[.light]:placeholder-gray-500 focus:outline-none focus:ring-2 ' +
    'focus:ring-cyan-500 focus:border-transparent transition-all'
const labelClassName = 'block text-sm font-medium text-slate-300 in-[.light]:text-gray-700 ml-1'

const LoginSection = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    })

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        // TODO: Implement login logic
        console.log('Login data:', formData)
    }

    return (
        <div className='w-full space-y-6'>
            <div className='text-center space-y-2'>
                <h2 className='text-3xl font-bold text-white in-[.light]:text-gray-900'>Welcome Back</h2>
            </div>

            <Button
                onClick={() => {
                    alert('Google Sign-In is not implemented yet.')
                }}
                className='w-full py-3 text-lg font-semibold shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-3'
                icon={<GoogleIcon />}
            >
                Sign in with Google
            </Button>

            <div className='flex items-center gap-4 py-2'>
                <div className='h-px bg-slate-700 in-[.light]:bg-gray-300 flex-1' />
                <span className='text-slate-500 text-sm'>OR</span>
                <div className='h-px bg-slate-700 in-[.light]:bg-gray-300 flex-1' />
            </div>

            <form onSubmit={handleSubmit} className='space-y-4 mt-8'>
                <div className='space-y-1'>
                    <label htmlFor='email' className={labelClassName}>
                        Email
                    </label>
                    <input
                        type='email'
                        id='email'
                        name='email'
                        value={formData.email}
                        onChange={handleChange}
                        className={inputClassName}
                        placeholder='Enter your email'
                        required
                    />
                </div>

                <div className='space-y-1'>
                    <label htmlFor='password' className={labelClassName}>
                        Password
                    </label>
                    <input
                        type='password'
                        id='password'
                        name='password'
                        value={formData.password}
                        onChange={handleChange}
                        className={inputClassName}
                        placeholder='Enter your password'
                        required
                    />
                </div>

                <div className='pt-4'>
                    <Button className='w-full py-3 text-lg font-semibold shadow-lg shadow-cyan-500/20'>
                        Sign In
                    </Button>
                </div>
            </form>

            <div className='text-center pt-2'>
                <p className='text-slate-400 text-sm'>
                    Don't have an account?{' '}
                    <a
                        href='/register'
                        className='text-cyan-400 hover:text-cyan-300 font-medium transition-colors'
                    >
                        Register here
                    </a>
                </p>
            </div>
        </div>
    )
}

export default LoginSection
