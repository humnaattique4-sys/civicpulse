import '@testing-library/jest-dom/vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import App from '../src/App.jsx'
import api from '../src/api'

vi.mock('../src/api', () => ({
  default: { post: vi.fn(), get: vi.fn(), patch: vi.fn() },
}))

const complaint = {
  id: 'abc', category: 'roads', priority: 'normal', status: 'open',
  location: 'Main Boulevard', ai_summary: 'Pothole',
}

beforeEach(() => vi.clearAllMocks())

describe('Dashboard filters, pagination and status changes', () => {
  it('shows the server 409 message exactly as returned', async () => {
    api.get.mockResolvedValue({ data: [complaint] })
    api.patch.mockRejectedValue({
      response: { data: { detail: 'Invalid transition from open to resolved' } },
    })
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Dashboard' }))
    const select = await screen.findByLabelText('Change status for abc')
    fireEvent.change(select, { target: { value: 'resolved' } })
    expect(await screen.findByText('Invalid transition from open to resolved')).toBeInTheDocument()
  })

  it('sends the chosen filter to the API', async () => {
    api.get.mockResolvedValue({ data: [complaint] })
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Dashboard' }))
    await screen.findByText('Main Boulevard')
    fireEvent.change(screen.getByLabelText('Priority'), { target: { value: 'high' } })
    await waitFor(() =>
      expect(api.get).toHaveBeenLastCalledWith(
        expect.stringContaining('priority=high')
      )
    )
  })

  it('disables Previous on page 1 and moves to page 2 with Next', async () => {
    api.get.mockResolvedValue({
      data: Array.from({ length: 10 }, (_, i) => ({ ...complaint, id: String(i) })),
    })
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Dashboard' }))
    await screen.findAllByText('Main Boulevard')
    expect(screen.getByRole('button', { name: 'Previous' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(await screen.findByText('Page 2')).toBeInTheDocument()
  })
})

describe('Stats page', () => {
  it('shows the cache status from the X-Cache header', async () => {
    api.get.mockResolvedValue({
      data: { by_category: { water: 3 }, by_priority: { high: 3 } },
      headers: { 'x-cache': 'HIT' },
    })
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Stats' }))
    expect(await screen.findByText('HIT')).toBeInTheDocument()
    expect(screen.getByText('water: 3')).toBeInTheDocument()
  })
})

describe('Error boundary', () => {
  it('shows a fallback instead of crashing when a child throws', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    api.get.mockImplementation(() => { throw new Error('boom') })
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Dashboard' }))
    expect(await screen.findByText('Something went wrong.')).toBeInTheDocument()
  })
})
