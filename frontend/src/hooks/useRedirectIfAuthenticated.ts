import { useEffect } from 'react'

const useRedirectIfAuthenticated = (redirectTo: string = '/home') => {
    useEffect(() => {
        const token = localStorage.getItem('access_token')
        if (token) {
            window.location.href = redirectTo
        }
    }, [redirectTo])
}

export default useRedirectIfAuthenticated
