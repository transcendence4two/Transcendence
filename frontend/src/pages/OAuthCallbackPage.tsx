import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const OAuthCallbackPage = () => {
    const navigate = useNavigate()
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const params = new URLSearchParams(window.location.search)
        const code = params.get('code')
        const errorParam = params.get('error')

        if (errorParam) {
            setError('GitHub authorization was denied.')
            return
        }

        if (!code) {
            setError('No authorization code received from GitHub.')
            return
        }

        fetch('/api/users/oauth/github/callback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
        })
            .then(async res => {
                const data = await res.json()
                if (!res.ok) {
                    throw new Error(data.detail || 'OAuth login failed.')
                }
                return data
            })
            .then(data => {
                localStorage.setItem('access_token', data.access_token)
                localStorage.setItem('user', JSON.stringify(data.user))
                navigate('/home')
            })
            .catch(err => {
                setError(err.message)
            })
    }, [navigate])

    if (error) {
        return (
            <div className='min-h-screen flex items-center justify-center bg-slate-950'>
                <div className='text-center space-y-4'>
                    <p className='text-red-400 text-lg'>{error}</p>
                    <a href='/login' className='text-cyan-400 hover:text-cyan-300 underline'>
                        Back to login
                    </a>
                </div>
            </div>
        )
    }

    return (
        <div className='min-h-screen flex items-center justify-center bg-slate-950'>
            <p className='text-slate-300 text-lg animate-pulse'>Signing you in with GitHub...</p>
        </div>
    )
}

export default OAuthCallbackPage
