import { vi } from 'vitest'
import type { RealtimeChannel, RealtimePostgresChangesPayload } from '@supabase/supabase-js'

export interface MockRealtimeChannel extends RealtimeChannel {
  callback: ((payload: RealtimePostgresChangesPayload<unknown>) => void) | null
}

export const createMockChannel = (channelName: string): MockRealtimeChannel => {
  const channel: MockRealtimeChannel = {
    topic: channelName,
    callback: null,
    on: vi.fn((event, config, callback) => {
      if (event === 'postgres_changes' && typeof callback === 'function') {
        channel.callback = callback as (payload: RealtimePostgresChangesPayload<unknown>) => void
      }
      return channel
    }),
    subscribe: vi.fn((callback) => {
      if (callback) callback('SUBSCRIBED', undefined)
      return channel
    }),
    unsubscribe: vi.fn().mockReturnThis(),
  } as unknown as MockRealtimeChannel
  return channel
}

export const mockSupabaseClient = {
  from: vi.fn(() => ({
    select: vi.fn().mockReturnThis(),
    insert: vi.fn().mockReturnThis(),
    update: vi.fn().mockReturnThis(),
    delete: vi.fn().mockReturnThis(),
    eq: vi.fn().mockReturnThis(),
    neq: vi.fn().mockReturnThis(),
    gt: vi.fn().mockReturnThis(),
    gte: vi.fn().mockReturnThis(),
    lt: vi.fn().mockReturnThis(),
    lte: vi.fn().mockReturnThis(),
    like: vi.fn().mockReturnThis(),
    ilike: vi.fn().mockReturnThis(),
    is: vi.fn().mockReturnThis(),
    in: vi.fn().mockReturnThis(),
    contains: vi.fn().mockReturnThis(),
    containedBy: vi.fn().mockReturnThis(),
    rangeGt: vi.fn().mockReturnThis(),
    rangeGte: vi.fn().mockReturnThis(),
    rangeLt: vi.fn().mockReturnThis(),
    rangeLte: vi.fn().mockReturnThis(),
    rangeAdjacent: vi.fn().mockReturnThis(),
    overlaps: vi.fn().mockReturnThis(),
    textSearch: vi.fn().mockReturnThis(),
    match: vi.fn().mockReturnThis(),
    not: vi.fn().mockReturnThis(),
    or: vi.fn().mockReturnThis(),
    filter: vi.fn().mockReturnThis(),
    order: vi.fn().mockReturnThis(),
    limit: vi.fn().mockReturnThis(),
    range: vi.fn().mockReturnThis(),
    single: vi.fn().mockResolvedValue({ data: null, error: null }),
    maybeSingle: vi.fn().mockResolvedValue({ data: null, error: null }),
    csv: vi.fn().mockResolvedValue({ data: null, error: null }),
    then: vi.fn((callback) => callback({ data: [], error: null })),
  })),
  channel: vi.fn((name: string) => createMockChannel(name)),
  removeChannel: vi.fn(),
  removeAllChannels: vi.fn(),
  getChannels: vi.fn().mockReturnValue([]),
}

export const createMockSupabaseClient = () => ({ ...mockSupabaseClient })
