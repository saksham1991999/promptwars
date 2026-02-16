/**
 * Morale utilities
 */

/** Morale categories */
export type MoraleCategory = 'high' | 'medium' | 'low' | 'critical';

/**
 * Get morale category from value
 */
export function getMoraleCategory(morale: number): MoraleCategory {
  if (morale >= 70) return 'high';
  if (morale >= 40) return 'medium';
  if (morale >= 20) return 'low';
  return 'critical';
}

/**
 * Get CSS class for morale value
 */
export function getMoraleClass(morale: number): string {
  const category = getMoraleCategory(morale);
  return `morale-${category}`;
}

/**
 * Get human-readable morale label
 */
export function getMoraleLabel(morale: number): string {
  const category = getMoraleCategory(morale);
  const labels: Record<MoraleCategory, string> = {
    high: 'High',
    medium: 'Medium',
    low: 'Low',
    critical: 'Critical',
  };
  return labels[category];
}
