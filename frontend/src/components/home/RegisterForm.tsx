import { useState } from 'react'
import Button from '../common/Button'
import { GoogleIcon } from '../icons/Icons'

const inputClassName =
    'w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-xl ' +
    'text-white placeholder-slate-500 focus:outline-none focus:ring-2 ' +
    'focus:ring-cyan-500 focus:border-transparent transition-all'
const labelClassName = 'block text-sm font-medium text-slate-300 ml-1'

const RegisterForm = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    })
    const [errors, setErrors] = useState<{ [key: string]: string }>({})

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
        // Clear error when user types
        if (errors[name] || errors['confirmPassword']) {
            setErrors(prev => ({ ...prev, [name]: '', confirmPassword: '' }))
        }
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        const newErrors: { [key: string]: string } = {}

        // Basic email validation
        if (!formData.email.includes('@')) {
            newErrors.email = 'Please enter a valid email address'
        }

        // Password match validation
        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match'
        }

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors)
            return
        }

        console.log('Form submitted:', formData)
		alert('Registration successful!')
        window.location.href = '/'
    }

    return (
        <div className='w-full space-y-6'>
            <div className='text-center space-y-2'>
                <h2 className='text-3xl font-bold text-white'>Create Account</h2>
            </div>

            <Button
                onClick={() => {
                    alert('Google Sign-In is not implemented yet. Please use the form below to register.')
                }}
                className='w-full py-3 text-lg font-semibold shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-3'
                icon={<GoogleIcon />}
            >
                Sign up with Google
            </Button>

            <div className='flex items-center gap-4 py-2'>
                <div className='h-px bg-slate-700 flex-1' />
                <span className='text-slate-500 text-sm'>OR</span>
                <div className='h-px bg-slate-700 flex-1' />
            </div>

            <form onSubmit={handleSubmit} className='space-y-4 mt-8'>

                <div className='space-y-1'>
                    <label htmlFor='username' className={labelClassName}>
                        Username
                    </label>
                    <input
                        type='text'
                        id='username'
                        name='username'
                        value={formData.username}
                        onChange={handleChange}
                        className={inputClassName}
                        placeholder='Enter your username'
                        required
                    />
                </div>

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
                        className={`${inputClassName} ${
                            errors.email ? 'border-red-500 focus:ring-red-500' : ''
                        }`}
                        placeholder='Enter your email'
                        required
                    />
                    {errors.email && (
                        <p className='text-red-500 text-xs ml-1'>{errors.email}</p>
                    )}
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

                <div className='space-y-1'>
                    <label htmlFor='confirmPassword' className={labelClassName}>
                        Confirm Password
                    </label>
                    <input
                        type='password'
                        id='confirmPassword'
                        name='confirmPassword'
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        className={`${inputClassName} ${
                            errors.confirmPassword ? 'border-red-500 focus:ring-red-500' : ''
                        }`}
                        placeholder='Confirm your password'
                        required
                    />
                    {errors.confirmPassword && (
                        <p className='text-red-500 text-xs ml-1'>{errors.confirmPassword}</p>
                    )}
                </div>

                <div className='pt-4'>
                    <Button className='w-full py-3 text-lg font-semibold shadow-lg shadow-cyan-500/20'>
                        Create Account
                    </Button>
                </div>
            </form>

            <div className='text-center pt-2'>
                <p className='text-slate-400 text-sm'>
                    Already have an account?{' '}Login{' '}
                    <a
                        href='/login'
                        className='text-cyan-400 hover:text-cyan-300 font-medium transition-colors'
                    >
                        here
                    </a>
                </p>
            </div>
        </div>
    )
}

export default RegisterForm
