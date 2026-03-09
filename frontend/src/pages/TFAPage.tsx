import Header from '../components/layout/Header'
import Footer from '../components/layout/Footer'
import TwoFactorAuthSection from '../components/home/TwoFactorAuthSection'

const inputClassName ='w-full max-w-125 border border-slate-700/50 in-[.light]:border-gray-200 bg-slate-800/50 in-[.light]:bg-white ' +
    'backdrop-blur-sm rounded-2xl p-8 shadow-2xl in-[.light]:shadow-xl'

const TFAPage = () => {
    return (
        <div className='container-main'>
            <Header />
            <main className='content-main grid place-items-center p-4 w-full'>
                <div className={inputClassName}>
                    <TwoFactorAuthSection />
                </div>
            </main>
            <Footer />
        </div>
    )
}

export default TFAPage
