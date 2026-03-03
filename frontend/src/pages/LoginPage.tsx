import Header from '../components/layout/Header'
import Footer from '../components/layout/Footer'
import LoginSection from '../components/home/LoginSection'
import useRedirectIfAuthenticated from '../hooks/useRedirectIfAuthenticated'

const inputClassName ='w-full max-w-125 border border-slate-700/50 bg-slate-800/50' +
    'backdrop-blur-sm rounded-2xl p-8 shadow-2xl light:shadow-xl'

const LoginPage = () => {
    useRedirectIfAuthenticated()

    return (
        <div className='container-main'>
            <Header />
            <main className='content-main grid place-items-center p-4 w-full'>
                <div className={inputClassName}>
                    <LoginSection />
                </div>
            </main>
            <Footer />
        </div>
    )
}

export default LoginPage
