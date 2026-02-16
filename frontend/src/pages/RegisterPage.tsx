import Header from '../components/layout/Header'
import Footer from '../components/layout/Footer'
import RegisterForm from '../components/home/RegisterForm'

const inputClassName ='w-full max-w-125 border border-slate-700/50 bg-slate-800/50' +
    'backdrop-blur-sm rounded-2xl p-8 shadow-2xl'

const RegisterPage = () => {
    return (
        <div className='container-main'>
            <Header />
            <main className='content-main grid place-items-center p-4 w-full'>
                <div className={inputClassName}>
                    <RegisterForm />
                </div>
            </main>
            <Footer />
        </div>
    )
}

export default RegisterPage
