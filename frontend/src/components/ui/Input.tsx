import React from 'react';
import './Input.css';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement | HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
  maxLength?: number;
  showCount?: boolean;
  inputType?: 'text' | 'textarea' | 'number' | 'email' | 'password';
}

export function Input({
  label,
  error,
  helperText,
  maxLength,
  showCount = false,
  inputType = 'text',
  className = '',
  value,
  ...props
}: InputProps) {
  const inputId = React.useId();
  const isTextarea = inputType === 'textarea';
  const currentLength = typeof value === 'string' ? value.length : 0;

  const inputProps = {
    id: inputId,
    className: `input ${error ? 'input-error' : ''} ${className}`,
    maxLength,
    value,
    ...props,
  };

  return (
    <div className="input-wrapper">
      {label && (
        <label htmlFor={inputId} className="input-label">
          {label}
        </label>
      )}

      {isTextarea ? (
        <textarea {...(inputProps as React.TextareaHTMLAttributes<HTMLTextAreaElement>)} />
      ) : (
        <input type={inputType} {...(inputProps as React.InputHTMLAttributes<HTMLInputElement>)} />
      )}

      <div className="input-footer">
        {error && <span className="input-error-text">{error}</span>}
        {!error && helperText && <span className="input-helper-text">{helperText}</span>}
        {showCount && maxLength && (
          <span className={`input-count ${currentLength >= maxLength ? 'input-count-limit' : ''}`}>
            {currentLength}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
}
