import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import RegisterForm from './RegisterForm'

const mockLocation = { href: '' }
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true
})
window.alert = vi.fn()

const mockFetch = vi.fn()
window.fetch = mockFetch

describe('RegisterForm Component', () => {

    beforeEach(() => {
        vi.clearAllMocks()
        mockLocation.href = ''

        mockFetch.mockResolvedValue({
            ok: true,
            json: async () => ({ id: '123', username: 'testuser' })
        })
    })

    afterEach(() => {
        vi.clearAllMocks()
    })

    it('renders form fields correctly', () => {
        render(<RegisterForm />)
        expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    })

    it('updates input values when typing', () => {
        render(<RegisterForm />)
        const usernameInput = screen.getByLabelText(/username/i)
        fireEvent.change(usernameInput, { target: { value: 'newuser' } })
        expect(usernameInput).toHaveValue('newuser')
    })

    it('shows error when passwords do not match', async () => {
        render(<RegisterForm />)

        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'user1' } })
        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@test.com' } })
        fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } })
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'different' } })

        fireEvent.click(screen.getByRole('button', { name: /create account/i }))

        await waitFor(() => {
            expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
        })
        expect(mockFetch).not.toHaveBeenCalled()
    })

    it('shows error when terms are not accepted', async () => {
        render(<RegisterForm />)

        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'validuser' } })
        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } })
        fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } })
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'password123' } })

        // Deliberately do NOT check the terms checkbox
        fireEvent.click(screen.getByRole('button', { name: /create account/i }))

        await waitFor(() => {
            expect(screen.getByText(/you must accept the terms of service to register/i)).toBeInTheDocument()
        })
        expect(mockFetch).not.toHaveBeenCalled()
    })

    it('submits form with valid data and redirects', async () => {
        render(<RegisterForm />)

        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'validuser' } })
        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } })
        fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } })
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'password123' } })
        fireEvent.click(screen.getByRole('checkbox'))

        fireEvent.click(screen.getByRole('button', { name: /create account/i }))

        await waitFor(() => {
            expect(mockFetch).toHaveBeenCalledWith('/api/users/register', expect.any(Object))
        })

        await waitFor(() => {
            expect(mockLocation.href).toBe('/login')
        })
    })

    it('displays API error message when registration fails due to username', async () => {
        const errorMessage = 'Username already taken'
        mockFetch.mockResolvedValueOnce({
            ok: false,
            json: async () => ({ detail: errorMessage })
        })

        render(<RegisterForm />)

        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'existinguser' } })
        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } })
        fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } })
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'password123' } })
        fireEvent.click(screen.getByRole('checkbox'))

        fireEvent.click(screen.getByRole('button', { name: /create account/i }))

        await waitFor(() => {
             expect(screen.getByText(errorMessage)).toBeInTheDocument()
        })
    })
})