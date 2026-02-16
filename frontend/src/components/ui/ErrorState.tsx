import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './Button';
import './ErrorState.css';

export interface ErrorStateProps {
  title?: string;
  message: string;
  retry?: () => void;
  retryLabel?: string;
}

export function ErrorState({
  title = 'Something went wrong',
  message,
  retry,
  retryLabel = 'Try again',
}: ErrorStateProps) {
  return (
    <div className="error-state" role="alert">
      <div className="error-state-icon">
        <AlertTriangle size={48} />
      </div>
      <h3 className="error-state-title">{title}</h3>
      <p className="error-state-message">{message}</p>
      {retry && (
        <Button onClick={retry} variant="secondary" icon={<RefreshCw size={16} />}>
          {retryLabel}
        </Button>
      )}
    </div>
  );
}
