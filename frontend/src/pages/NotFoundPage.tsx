import PageNavbar from '../components/common/PageNavbar'
import Footer from '../components/layout/Footer'

const NotFoundPage = () => {
    return (
        <div className='container-main'>
            <PageNavbar />
            <main className='content-main p-8'>
                <div className='max-w-4xl mx-auto bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-slate-700/50'>
                    <h1 className='heading-1'>404 Not Found</h1>
                    <p className='mb-4 text-gray-300'>
                        The page you are looking for does not exist or may have been moved.
                    </p>
                    <p className='text-gray-300'>
                        Please check the URL or return to the home page.
                        <a href="/" className='text-cyan-400 hover:text-cyan-300 transition-colors'> Go back home</a>.
                    </p>
                </div>
            </main>
            <Footer />
        </div>
    )
}

export default NotFoundPage
