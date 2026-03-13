import { useState } from 'react'
import Button from '../common/Button'
import { GitHubIcon } from '../icons/Icons'
import TermsOfServiceModal from './TermsOfServiceModal'

const inputClassName =
    'w-full px-4 py-3 bg-slate-900/50 [.light_&]:bg-gray-100 [.light_&]:border-gray-300 [.light_&]:text-gray-900 border border-slate-600 rounded-xl ' +
    'text-white placeholder-slate-500 [.light_&]:placeholder-gray-500 focus:outline-none focus:ring-2 ' +
    'focus:ring-cyan-500 focus:border-transparent transition-all'
const labelClassName = 'block text-sm font-medium text-slate-300 [.light_&]:text-gray-700 ml-1'

const RegisterForm = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    })
    const [acceptedTerms, setAcceptedTerms] = useState(false)
    const [showTermsModal, setShowTermsModal] = useState(false)
    const [errors, setErrors] = useState<{ [key: string]: string }>({})
    const [isLoading, setIsLoading] = useState(false)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
        // Clear error when user types
        if (errors[name] || errors['confirmPassword']) {
            setErrors(prev => ({ ...prev, [name]: '', confirmPassword: '' }))
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        const newErrors: { [key: string]: string } = {}

        if (!formData.email.includes('@')) {
            newErrors.email = 'Please enter a valid email address'
        }

        if (formData.username.length < 1 || formData.username.length > 255) {
            newErrors.username = 'Username must not exceed 255 characters'
        }

        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match'
        }

        if (formData.password.length < 6) {
            newErrors.password = 'Password must have at least 6 characters'
        } else if (formData.password.length > 255) {
            newErrors.password = 'Password must not exceed 255 characters'
        }

        if (!acceptedTerms) {
            newErrors.terms = 'You must accept the Terms of Service to register'
        }

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors)
            return
        }

        setIsLoading(true)

        try {
            const response = await fetch('/api/users/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password,
                    enable_2fa: true
                }),
            })

            const data = await response.json()

            if (!response.ok) {
                if (data.detail && typeof data.detail === 'string') {
                    if (data.detail.includes('Username')) {
                        setErrors(prev => ({ ...prev, username: data.detail }))
                    } else if (data.detail.includes('Email')) {
                        setErrors(prev => ({ ...prev, email: data.detail }))
                    } else {
                        alert(`Registration failed: ${data.detail}`)
                    }
                } else {
                    alert('Registration failed. Please try again.')
                }
                return
            }

            console.log('User registered:', data)
            alert('Registration successful! You will be redirected to login.')
            window.location.href = '/login'

        } catch (error) {
            console.error('Registration error:', error)
            alert('An error occurred during registration. Please check your connection.')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <>
            {showTermsModal && (
                <TermsOfServiceModal onClose={() => setShowTermsModal(false)} />
            )}

            <div className='w-full space-y-6'>
                <div className='text-center space-y-2'>
                    <h2 className='text-3xl font-bold text-white in-[.light]:text-gray-900'>Create Account</h2>
                </div>

                <Button
                    onClick={async () => {
                        const res = await fetch('/api/users/oauth/github/authorize')
                        const data = await res.json()
                        window.location.href = data.authorize_url
                    }}
                    className='w-full py-3 text-lg font-semibold shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-3'
                    icon={<GitHubIcon />}
                >
                    Sign up with GitHub
                </Button>

                <div className='flex items-center gap-4 py-2'>
                    <div className='h-px bg-slate-700 in-[.light]:bg-gray-300 flex-1' />
                    <span className='text-slate-500 text-sm'>OR</span>
                    <div className='h-px bg-slate-700 in-[.light]:bg-gray-300 flex-1' />
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
                            className={`${inputClassName} ${errors.username ? 'border-red-500 focus:ring-red-500' : ''
                                }`}
                            placeholder='Enter your username'
                            required
                        />
                        {errors.username && (
                            <p className='text-red-500 text-xs ml-1'>{errors.username}</p>
                        )}
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
                            className={`${inputClassName} ${errors.email ? 'border-red-500 focus:ring-red-500' : ''
                                }`}
                            placeholder='Enter your email'
                            disabled={isLoading}
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
                            className={`${inputClassName} ${errors.password ? 'border-red-500 focus:ring-red-500' : ''
                                }`}
                            placeholder='Enter your password'
                            disabled={isLoading}
                            required
                        />
                        {errors.password && (
                            <p className='text-red-500 text-xs ml-1'>{errors.password}</p>
                        )}
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
                            className={`${inputClassName} ${errors.confirmPassword ? 'border-red-500 focus:ring-red-500' : ''
                                }`}
                            placeholder='Confirm your password'
                            disabled={isLoading}
                            required
                        />
                        {errors.confirmPassword && (
                            <p className='text-red-500 text-xs ml-1'>{errors.confirmPassword}</p>
                        )}
                    </div>

                    <div className='space-y-1 pt-2'>
                        <label className={`flex items-start gap-3 cursor-pointer ${errors.terms ? 'text-red-500' : ''}`}>
                            <input
                                type='checkbox'
                                id='acceptTerms'
                                checked={acceptedTerms}
                                onChange={(e) => {
                                    setAcceptedTerms(e.target.checked)
                                    if (errors.terms) {
                                        setErrors(prev => ({ ...prev, terms: '' }))
                                    }
                                }}
                                className='mt-0.5 h-4 w-4 shrink-0 rounded border-slate-600 bg-slate-900/50 accent-cyan-500 cursor-pointer'
                            />
                            <span className='text-sm text-slate-400 in-[.light]:text-gray-600 leading-snug'>
                                I have read and agree to the{' '}
                                <button
                                    type='button'
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        setShowTermsModal(true)
                                    }}
                                    className='text-cyan-400 hover:text-cyan-300 in-[.light]:text-cyan-600 in-[.light]:hover:text-cyan-700 font-medium transition-colors underline underline-offset-2 cursor-pointer'
                                >
                                    Terms of Service
                                </button>
                            </span>
                        </label>
                        {errors.terms && (
                            <p className='text-red-500 text-xs ml-1'>{errors.terms}</p>
                        )}
                    </div>

                    <div className='pt-4'>
                        <Button
                            type='submit'
                            className={`w-full py-3 text-lg font-semibold shadow-lg shadow-cyan-500/20 ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Creating Account...' : 'Create Account'}
                        </Button>
                    </div>

                </form>

                <div className='text-center pt-2'>
                    <p className='text-slate-400 text-sm'>
                        Already have an account?{' '}
                        <a
                            href='/login'
                            className='text-cyan-400 hover:text-cyan-300 font-medium transition-colors'
                        >
                            Sign in here
                        </a>
                    </p>
                </div>
            </div>
        </>
    )
}

export default RegisterForm