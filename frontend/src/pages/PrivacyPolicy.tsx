import PageNavbar from '../components/common/PageNavbar'
import Footer from '../components/layout/Footer'

const PrivacyPolicy = () => {
    return (
        <div className='container-main'>
            <PageNavbar />
            <main className='content-main p-8'>
                <div className='max-w-4xl mx-auto bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-slate-700/50'>
                    <h1 className='heading-1'>Privacy Policy</h1>
                    <p className='mb-4 text-gray-300'>
                        Your privacy is important to us. This Privacy Policy explains how we collect, use, and protect your personal information when you use our website.
                    </p>
                    <h2 className='heading-2'>Information We Collect</h2>
                    <ul className='list-disc list-inside mb-4 text-gray-300'>
                        <li>Personal identification information (name, email address, phone number, etc.)</li>
                        <li>Usage data (pages visited, time spent on pages, etc.)</li>
                        <li>Cookies and tracking technologies</li>
                    </ul>
                    <h2 className='heading-2'>How We Use Your Information</h2>
                    <ul className='list-disc list-inside mb-4 text-gray-300'>
                        <li>To provide and maintain our services</li>
                        <li>To improve our website and user experience</li>
                        <li>To communicate with you regarding updates and promotions</li>
                    </ul>
                    <h2 className='heading-2'>Data Protection</h2>
                    <p className='mb-4 text-gray-300'>
                        We implement appropriate security measures to protect your personal information from unauthorized access, alteration, disclosure, or destruction.
                    </p>
                    <h2 className='heading-2'>Your Rights</h2>
                    <p className='mb-4 text-gray-300'>
                        You have the right to access, update, or delete your personal information. You can also opt-out of receiving promotional communications from us.
                    </p>
                    <h2 className='heading-2'>Contact Us</h2>
                    <p className='text-gray-300'>
                        If you have any questions or concerns about this Privacy Policy, please contact us at:
                        <a href="mailto:support@transcendence42.com" className='text-cyan-400 hover:text-cyan-300 transition-colors'> support@transcendence42.com</a>.
                    </p>
                </div>
            </main>
            <Footer />
        </div>
    )
}

export default PrivacyPolicy
