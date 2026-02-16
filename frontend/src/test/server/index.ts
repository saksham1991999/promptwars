import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
export { handlers, resetMockStore, addMockGame, getMockGame } from './handlers'
