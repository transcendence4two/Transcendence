import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import Button from '../common/Button'

interface TermsOfServiceModalProps {
    onClose: () => void
}

const TermsOfServiceModal = ({ onClose }: TermsOfServiceModalProps) => {
    const modalRef = useRef<HTMLDivElement>(null)

    // Close on Escape key
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose()
        }
        document.addEventListener('keydown', handleKeyDown)
        return () => document.removeEventListener('keydown', handleKeyDown)
    }, [onClose])

    // Prevent body scroll while modal is open
    useEffect(() => {
        document.body.style.overflow = 'hidden'
        return () => { document.body.style.overflow = '' }
    }, [])

    // Close on backdrop click (but not on modal content click)
    const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
            onClose()
        }
    }

    return createPortal(
        <div
            className='fixed inset-0 z-50 flex items-center justify-center p-6'
            onClick={handleBackdropClick}
        >
            {/* Backdrop */}
            <div className='absolute inset-0 bg-black/70 backdrop-blur-sm' aria-hidden='true' />

            {/* Modal */}
            <div
                ref={modalRef}
                role='dialog'
                aria-modal='true'
                aria-labelledby='tos-title'
                className='relative w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl border border-slate-700/50 in-[.light]:border-gray-200 bg-slate-900 in-[.light]:bg-white shadow-2xl'
            >
                {/* Header */}
                <div className='flex items-center justify-between px-8 py-5 border-b border-slate-700/50 in-[.light]:border-gray-200 shrink-0'>
                    <h2
                        id='tos-title'
                        className='text-xl font-bold text-white in-[.light]:text-gray-900'
                    >
                        Terms of Service
                    </h2>
                    <button
                        onClick={onClose}
                        aria-label='Close terms of service'
                        className='flex items-center justify-center w-8 h-8 rounded-lg text-slate-400 in-[.light]:text-gray-500 hover:text-white in-[.light]:hover:text-gray-900 hover:bg-slate-700/60 in-[.light]:hover:bg-gray-100 transition-colors cursor-pointer'
                    >
                        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' className='w-5 h-5'>
                            <path d='M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z' />
                        </svg>
                    </button>
                </div>

                {/* Scrollable body */}
                <div className='overflow-y-auto px-8 py-6 space-y-6 text-base text-slate-300 in-[.light]:text-gray-700 leading-relaxed'>

                    <p>
                        Welcome to <span className='font-semibold text-white in-[.light]:text-gray-900'>Transcendence</span>.
                        By creating an account you agree to be bound by these Terms of Service.
                        Please read them carefully before registering.
                    </p>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>1. Acceptance of Terms</h3>
                        <p>
                            By accessing or using the platform, you confirm that you are at least 13 years old,
                            have read and understood these terms, and agree to be legally bound by them.
                            If you do not agree, you may not use this service.
                        </p>
                    </section>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>2. User Accounts</h3>
                        <p>
                            You are responsible for maintaining the confidentiality of your account credentials.
                            You agree not to share your password or allow others to access your account.
                            You are solely responsible for all activity that occurs under your account.
                        </p>
                    </section>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>3. Acceptable Use</h3>
                        <p>You agree not to:</p>
                        <ul className='list-disc list-inside space-y-1.5 pl-2'>
                            <li>Use the platform for any unlawful purpose or in violation of any regulations.</li>
                            <li>Harass, abuse, threaten, or intimidate other users.</li>
                            <li>Attempt to gain unauthorized access to any part of the platform or its infrastructure.</li>
                            <li>Reverse engineer, decompile, or otherwise attempt to extract the source code of the platform.</li>
                            <li>Use automated tools (bots, scrapers, etc.) to interact with the service without prior written consent.</li>
                        </ul>
                    </section>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>4. Privacy</h3>
                        <p>
                            Your use of the platform is also governed by our Privacy Policy, which is incorporated
                            into these Terms by reference. By using the service you consent to the collection and
                            use of your data as described therein.
                        </p>
                    </section>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>5. Intellectual Property</h3>
                        <p>
                            All content, trademarks, logos, and software associated with the platform are the
                            property of Transcendence or its licensors. You may not reproduce, distribute, or
                            create derivative works without express written permission.
                        </p>
                    </section>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>6. Termination</h3>
                        <p>
                            We reserve the right to suspend or permanently terminate your account at our sole
                            discretion, without notice, if you violate these Terms or engage in conduct we
                            determine to be harmful to the platform or its users.
                        </p>
                    </section>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>7. Disclaimer of Warranties</h3>
                        <p>
                            The platform is provided on an "as is" and "as available" basis without warranties of
                            any kind, either express or implied. We do not warrant that the service will be
                            uninterrupted, error-free, or free of harmful components.
                        </p>
                    </section>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>8. Limitation of Liability</h3>
                        <p>
                            To the fullest extent permitted by law, Transcendence shall not be liable for any
                            indirect, incidental, special, consequential, or punitive damages arising from your
                            use of or inability to use the service.
                        </p>
                    </section>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>9. Changes to Terms</h3>
                        <p>
                            We may update these Terms from time to time. Continued use of the platform after
                            changes are posted constitutes your acceptance of the revised Terms. We encourage
                            you to review this page periodically.
                        </p>
                    </section>

                    <section className='space-y-2'>
                        <h3 className='font-semibold text-white in-[.light]:text-gray-900'>10. Contact</h3>
                        <p>
                            If you have any questions about these Terms, please reach out to us at{' '}
                            <a
                                href='mailto:trancendencefortytwo@gmail.com'
                                className='text-cyan-400 hover:text-cyan-300 in-[.light]:text-cyan-600 in-[.light]:hover:text-cyan-700 transition-colors underline underline-offset-2'
                            >
                              trancendencefortytwo@gmail.com
                            </a>.
                        </p>
                    </section>

                    <div className='h-2' />
                </div>

                {/* Footer */}
                <div className='flex justify-end gap-3 px-8 py-5 border-t border-slate-700/50 in-[.light]:border-gray-200 shrink-0'>
                    <Button
                        onClick={onClose}
                        variant='secondary'
                        className='px-5 py-2 text-sm font-medium'
                    >
                        Close
                    </Button>
                </div>
            </div>
        </div>,
        document.body
    )
}

export default TermsOfServiceModal
