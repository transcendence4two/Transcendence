import { render, screen, fireEvent } from '@testing-library/react'
import Button from './Button'
import { describe, it, expect, vi } from 'vitest'
import React from 'react'

describe('Button Component', () => {
    // 1. Renderização Básica
    it('renders children correctly', () => {
        render(<Button>Click me</Button>)
        expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
    })

    // 2. Interação (Click)
    it('calls onClick handler when clicked', () => {
        const handleClick = vi.fn() // Cria uma função "espiã"
        render(<Button onClick={handleClick}>Click me</Button>)

        fireEvent.click(screen.getByRole('button'))

        expect(handleClick).toHaveBeenCalledTimes(1)
    })

    // 3. Estilos (Variants)
    it('applies default primary variant class', () => {
        render(<Button>Primary</Button>)
        const button = screen.getByRole('button')
        expect(button).toHaveClass('btn-primary')
    })

    it('applies secondary variant class', () => {
        render(<Button variant="secondary">Secondary</Button>)
        const button = screen.getByRole('button')
        expect(button).toHaveClass('btn-secondary')
    })

    it('applies hero variant class', () => {
        render(<Button variant="hero">Hero</Button>)
        const button = screen.getByRole('button')
        expect(button).toHaveClass('btn-hero')
    })

    // 4. Classes Customizadas
    it('merges custom className with variant class', () => {
        render(<Button className="custom-test-class">Custom</Button>)
        const button = screen.getByRole('button')
        expect(button).toHaveClass('btn-primary') // Mantém o padrão
        expect(button).toHaveClass('custom-test-class') // Adiciona o custom
    })

    // 5. Estado Desabilitado
    it('is disabled when disabled prop is true', () => {
        render(<Button disabled>Disabled</Button>)
        const button = screen.getByRole('button')
        expect(button).toBeDisabled()
    })

    it('does not call onClick when disabled', () => {
        const handleClick = vi.fn()
        render(<Button disabled onClick={handleClick}>Disabled</Button>)

        fireEvent.click(screen.getByRole('button'))

        expect(handleClick).not.toHaveBeenCalled()
    })

    // 6. Ícones
    it('renders icon when provided', () => {
        const MockIcon = <span data-testid="test-icon">icon</span>
        render(<Button icon={MockIcon}>With Icon</Button>)

        expect(screen.getByTestId('test-icon')).toBeInTheDocument()
        expect(screen.getByText('With Icon')).toBeInTheDocument()
    })
})
