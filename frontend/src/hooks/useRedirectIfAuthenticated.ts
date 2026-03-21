import { useEffect } from 'react'
import { isTokenValid } from '../utils/auth'

const useRedirectIfAuthenticated = (redirectTo: string = '/home') => {
    useEffect(() => {
        const token = localStorage.getItem('access_token')
        if (isTokenValid(token)) {
            window.location.href = redirectTo
        }
    }, [redirectTo])
}

export default useRedirectIfAuthenticated
