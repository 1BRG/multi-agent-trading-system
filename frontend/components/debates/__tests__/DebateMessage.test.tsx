import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DebateMessage } from '../DebateMessage';

describe('DebateMessage', () => {
  it('renders a Bull Analyst message correctly', () => {
    const message = {
      id: 1,
      session_id: 1,
      agent_name: 'Bull Analyst',
      agent_role: 'bullish',
      round_number: 1,
      content: 'This stock has strong growth potential.\n\nRevenue is up 20%.',
      created_at: '2025-01-01T00:00:00Z',
    };

    const { container } = render(<DebateMessage message={message} />);

    expect(screen.getByText('🐂 Bull Analyst')).toBeDefined();
    expect(screen.getByText('Opening Argument')).toBeDefined();
    expect(screen.getByText('This stock has strong growth potential.')).toBeDefined();
    expect(screen.getByText('Revenue is up 20%.')).toBeDefined();
    
    // Check if correct css class is applied
    expect(container.querySelector('.debate-msg-bull')).toBeDefined();
  });

  it('renders a Bear Analyst message correctly', () => {
    const message = {
      id: 2,
      session_id: 1,
      agent_name: 'Bear Analyst',
      agent_role: 'bearish',
      round_number: 3,
      content: 'The valuation is too high.',
      created_at: '2025-01-01T00:00:00Z',
    };

    const { container } = render(<DebateMessage message={message} />);

    expect(screen.getByText('🐻 Bear Analyst')).toBeDefined();
    expect(screen.getByText('Rebuttal')).toBeDefined();
    expect(screen.getByText('The valuation is too high.')).toBeDefined();
    
    expect(container.querySelector('.debate-msg-bear')).toBeDefined();
  });

  it('renders a Judge message correctly', () => {
    const message = {
      id: 3,
      session_id: 1,
      agent_name: 'Judge',
      agent_role: 'judge',
      round_number: 5,
      content: 'I have weighed the evidence.',
      created_at: '2025-01-01T00:00:00Z',
    };

    const { container } = render(<DebateMessage message={message} />);

    expect(screen.getByText('⚖️ Judge')).toBeDefined();
    expect(screen.getByText('Final Verdict')).toBeDefined();
    
    expect(container.querySelector('.debate-msg-judge')).toBeDefined();
  });
});
