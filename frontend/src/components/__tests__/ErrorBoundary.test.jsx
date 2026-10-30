import { render, screen } from '@testing-library/react';
import React from 'react';
import ErrorBoundary from '../ErrorBoundary';
import { describe, it, expect, vi } from 'vitest';

const ProblemChild = () => {
  throw new Error('Test Error');
};

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div data-testid="safe">Safe content</div>
      </ErrorBoundary>
    );
    expect(screen.getByTestId('safe')).toHaveTextContent('Safe content');
  });

  it('renders error message when there is an error', () => {
    // Suppress console.error for this expected error test
    const consoleSpy = vi.spyOn(console, 'error');
    consoleSpy.mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ProblemChild />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    
    consoleSpy.mockRestore();
  });
});
