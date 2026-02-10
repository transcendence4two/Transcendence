import { Link } from 'react-router-dom'

const Footer = () => {
    return (
        <footer className='footer-main'>
            <Link to="/privacy-policy" className='text-sm link-base'>
                Privacy Policy
            </Link>
            <p className='text-sm'>© 2026 Transcendence 42 Rio C2G1.</p>
            <p className='text-sm'>All rights reserved.</p>
        </footer>
    )
}

export default Footer
