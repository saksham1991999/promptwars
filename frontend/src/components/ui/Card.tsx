import React from 'react';
import './Card.css';

export type CardVariant = 'default' | 'glass' | 'elevated';
export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  padding?: CardPadding;
  children: React.ReactNode;
}

export function Card({
  variant = 'default',
  padding = 'md',
  className = '',
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={`card card-${variant} card-padding-${padding} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
