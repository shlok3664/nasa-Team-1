import { Component, type ErrorInfo, type PropsWithChildren } from 'react';
import { ErrorState } from './ui';

type ErrorBoundaryState = { error: Error | null };

export class ErrorBoundary extends Component<PropsWithChildren, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Earth Twin Engine page failed to render.', error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <ErrorState
          message={this.state.error.message}
          onRetry={() => this.setState({ error: null })}
        />
      );
    }
    return this.props.children;
  }
}
