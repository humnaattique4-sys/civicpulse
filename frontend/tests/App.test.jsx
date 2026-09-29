import '@testing-library/jest-dom/vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import App from '../src/App.jsx'
import api from '../src/api'

vi.mock('../src/api', () => ({
  default: { post: vi.fn(), get: vi.fn() },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('CivicPulse App', () => {
  it('renders the title and navigation buttons', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: 'CivicPulse' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Dashboard' })).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: 'Submit' }).length).toBe(2)
  })

  it('shows the submit form by default', () => {
    const { container } = render(<App />)
    expect(screen.getByText('Submit a Complaint')).toBeInTheDocument()
    expect(container.querySelector('textarea')).toBeInTheDocument()
    expect(container.querySelector('table')).not.toBeInTheDocument()
  })

  it('submits a complaint and displays the triage result', async () => {
    api.post.mockResolvedValue({
      data: {
        category: 'water',
        priority: 'high',
        ai_summary: 'Burst water main',
        triaged_by: 'rules',
      },
    })
    const { container } = render(<App />)
    fireEvent.change(container.querySelector('textarea'), {
      target: { value: 'Burst water main flooding Street 12' },
    })
    fireEvent.change(container.querySelectorAll('input')[0], {
      target: { value: 'Street 12' },
    })
    fireEvent.submit(container.querySelector('form'))

    await waitFor(() =>
      expect(api.post).toHaveBeenCalledWith('/api/complaints', {
        text: 'Burst water main flooding Street 12',
        location: 'Street 12',
        reporter_contact: null,
      })
    )
    expect(await screen.findByText('water')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
    expect(screen.getByText('rules')).toBeInTheDocument()
  })

  it('shows the server error message when submission fails', async () => {
    api.post.mockRejectedValue({ response: { data: { detail: 'Rate limited' } } })
    const { container } = render(<App />)
    fireEvent.change(container.querySelector('textarea'), {
      target: { value: 'Some long enough complaint text' },
    })
    fireEvent.change(container.querySelectorAll('input')[0], {
      target: { value: 'Park Road' },
    })
    fireEvent.submit(container.querySelector('form'))
    expect(await screen.findByText('Rate limited')).toBeInTheDocument()
  })

  it('loads and lists complaints on the dashboard', async () => {
    api.get.mockResolvedValue({
      data: [
        {
          id: '1',
          category: 'roads',
          priority: 'normal',
          status: 'open',
          location: 'Main Boulevard',
          ai_summary: 'Pothole on main road',
        },
      ],
    })
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Dashboard' }))
    expect(await screen.findByText('Main Boulevard')).toBeInTheDocument()
    expect(screen.getByText('Pothole on main road')).toBeInTheDocument()
  })

  it('shows an error when the dashboard fails to load', async () => {
    api.get.mockRejectedValue(new Error('network down'))
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Dashboard' }))
    expect(await screen.findByText('Could not load complaints')).toBeInTheDocument()
  })
})