import React from 'react';
import './Skeleton.css';

export type SkeletonVariant = 'text' | 'circular' | 'rectangular';

export interface SkeletonProps {
  variant?: SkeletonVariant;
  width?: string | number;
  height?: string | number;
  count?: number;
  className?: string;
  style?: React.CSSProperties;
}

export function Skeleton({
  variant = 'text',
  width,
  height,
  count = 1,
  className = '',
  style: passedStyle,
}: SkeletonProps) {
  const style: React.CSSProperties = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  const skeletonElement = (
    <div
      className={`skeleton skeleton-${variant} ${className}`}
      style={{ ...style, ...passedStyle }}
      aria-label="Loading"
      role="status"
    />
  );

  if (count === 1) {
    return skeletonElement;
  }

  return (
    <div className="skeleton-group">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="skeleton-item">
          {skeletonElement}
        </div>
      ))}
    </div>
  );
}
