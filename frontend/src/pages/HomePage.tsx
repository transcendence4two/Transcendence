import Header from '../components/layout/Header'
import Footer from '../components/layout/Footer'
import HeroSection from '../components/home/HeroSection'

const HomePage = () => {
    return (
        <div className='container-main'>
            <Header />
            <main className='content-main flex items-center justify-center p-8'>
                <div className='max-w-4xl mx-auto bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-slate-700/50'>
                    <HeroSection />
                </div>
            </main>
            <Footer />
        </div>
    )
}

export default HomePage
