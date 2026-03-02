import Button from '../common/Button'
import { useState, useRef } from 'react'
import type { KeyboardEvent, ClipboardEvent } from 'react'

const inputClassName =
    'w-14 h-14 text-center text-2xl font-bold bg-slate-900/50 [.light_&]:bg-gray-100 [.light_&]:border-gray-300 [.light_&]:text-gray-900 border border-slate-600 rounded-xl ' +
    'text-white placeholder-slate-500 [.light_&]:placeholder-gray-500 focus:outline-none focus:ring-2 ' +
    'focus:ring-cyan-500 focus:border-transparent transition-all'

const TwoFactorAuthSection = () => {
    const [otp, setOtp] = useState<string[]>(Array(6).fill(''))
    const [error, setError] = useState<string>('')
    const [isLoading, setIsLoading] = useState(false)
    const inputRefs = useRef<(HTMLInputElement | null)[]>([])

    const handleChange = (index: number, value: string) => {
        if (value && !/^\d$/.test(value)) return

        const newOtp = [...otp]
        newOtp[index] = value
        setOtp(newOtp)

        if (error) setError('')

        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus()
        }
    }

    const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs.current[index - 1]?.focus()
        }

        if (e.key === 'ArrowRight' && index < 5) {
            inputRefs.current[index + 1]?.focus()
        }

        if (e.key === 'ArrowLeft' && index > 0) {
            inputRefs.current[index - 1]?.focus()
        }
    }

    const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
        e.preventDefault()
        const pastedData = e.clipboardData.getData('text').slice(0, 6)

        if (!/^\d+$/.test(pastedData)) return

        const newOtp = [...otp]
        pastedData.split('').forEach((char, index) => {
            if (index < 6) {
                newOtp[index] = char
            }
        })
        setOtp(newOtp)

        const nextIndex = Math.min(pastedData.length, 5)
        inputRefs.current[nextIndex]?.focus()
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        const otpCode = otp.join('')

        if (otpCode.length !== 6) {
            setError('Please enter all 6 digits')
            return
        }

        setIsLoading(true)

        try {
            const tempToken = localStorage.getItem('temp_token')

            if (!tempToken) {
                setError('Session expired. Please login again.')
                setTimeout(() => {
                    window.location.href = '/login'
                }, 2000)
                return
            }

            const response = await fetch('/api/users/verify-2fa', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    temporary_token: tempToken,
                    otp_code: otpCode,
                }),
            })

            const data = await response.json()

            if (!response.ok) {
                if (data.detail) {
                    setError(data.detail)
                } else {
                    setError('Invalid verification code. Please try again.')
                }
                setOtp(Array(6).fill(''))
                inputRefs.current[0]?.focus()
                return
            }

            if (data.access_token) {
                localStorage.removeItem('temp_token')
                localStorage.setItem('access_token', data.access_token)
                localStorage.setItem('user', JSON.stringify(data.user))

                window.location.href = '/home'
            }

        } catch (error) {
            console.error('2FA verification error:', error)
            setError('Connection error. Please try again.')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className='w-full space-y-6'>
            <div className='text-center space-y-2'>
                <h2 className='text-3xl font-bold text-white in-[.light]:text-gray-900'>
                    Two-Factor Authentication
                </h2>
                <p className='text-slate-400 in-[.light]:text-gray-600 text-sm'>
                    Enter the 6-digit code sent to your email
                </p>
            </div>

            <form onSubmit={handleSubmit} className='space-y-6 mt-8'>
                {error && (
                    <div className='bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded-xl text-sm text-center'>
                        {error}
                    </div>
                )}

                <div className='flex justify-center gap-3'>
                    {otp.map((digit, index) => (
                        <input
                            key={index}
                            ref={(el) => { inputRefs.current[index] = el }}
                            type='text'
                            inputMode='numeric'
                            maxLength={1}
                            value={digit}
                            onChange={(e) => handleChange(index, e.target.value)}
                            onKeyDown={(e) => handleKeyDown(index, e)}
                            onPaste={index === 0 ? handlePaste : undefined}
                            className={inputClassName}
                            disabled={isLoading}
                            autoFocus={index === 0}
                        />
                    ))}
                </div>

                <div className='pt-4'>
                    <Button
                        type='submit'
                        className='w-full py-3 text-lg font-semibold shadow-lg shadow-cyan-500/20'
                        disabled={isLoading || otp.some(digit => !digit)}
                    >
                        {isLoading ? 'Verifying...' : 'Verify Code'}
                    </Button>
                </div>
            </form>

            <div className='text-center pt-2'>
                <p className='text-slate-400 in-[.light]:text-gray-600 text-sm'>
                    Didn't receive the code?{' '}
                    <button
                        type='button'
                        className='text-cyan-400 hover:text-cyan-300 font-medium transition-colors'
                        onClick={() => {
                            // TODO: Implement resend OTP functionality
                            alert('Resend functionality not implemented yet')
                        }}
                    >
                        Resend
                    </button>
                </p>
                <p className='text-slate-500 in-[.light]:text-gray-500 text-xs mt-2'>
                    <a
                        href='/login'
                        className='text-cyan-400 hover:text-cyan-300 transition-colors'
                    >
                        Back to login
                    </a>
                </p>
            </div>
        </div>
    )
}

export default TwoFactorAuthSection
