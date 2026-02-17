import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import RegisterForm from './RegisterForm'
import React from 'react'

// Mock do fetch global
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock do window.location e alert
const mockLocation = { href: '' }
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true
})
window.alert = vi.fn()

describe('RegisterForm Component', () => {

    beforeEach(() => {
        vi.clearAllMocks()
        mockFetch.mockResolvedValue({
            ok: true,
            json: async () => ({ id: '123', username: 'testuser' })
        })
    })

    // 1. Renderização Inicial
    it('renders form fields correctly', () => {
        render(<RegisterForm />)

        expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
    })

    // 2. Atualização de Inputs
    it('updates input values when typing', () => {
        render(<RegisterForm />)
        const usernameInput = screen.getByLabelText(/username/i)
        fireEvent.change(usernameInput, { target: { value: 'newuser' } })
        expect(usernameInput).toHaveValue('newuser')
    })

    // 3. Validação de Senha Incompatível
    it('shows error when passwords do not match', async () => {
        render(<RegisterForm />)

        // Preencher outros campos obrigatórios para evitar outros erros de validação
        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'user1' } })
        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@test.com' } })

        // Simular senhas diferentes
        fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } })
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'different' } })

        fireEvent.click(screen.getByRole('button', { name: /create account/i }))

        await waitFor(() => {
            expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
        })
        expect(mockFetch).not.toHaveBeenCalled()
    })

    it('submits form with valid data and redirects', async () => {
        render(<RegisterForm />)
        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'validuser' } })
        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } })
        fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } })
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'password123' } })

        fireEvent.click(screen.getByRole('button', { name: /create account/i }))

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

        fireEvent.click(screen.getByRole('button', { name: /create account/i }))

    })
})
