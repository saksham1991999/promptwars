import { http, HttpResponse } from 'msw'
import type { Game, ChatMessage, CommandResponse, PersuasionResponse } from '../../types/game'
import { createGame, createBoardState } from '../factories/game'
import { createChatMessage } from '../factories/chat'

const API_BASE = 'http://localhost:8000/api/v1'

// Mock games store
const games = new Map<string, Game>()
const chatHistory = new Map<string, ChatMessage[]>()

export const handlers = [
  // Health check
  http.get(`${API_BASE}/health`, () => {
    return HttpResponse.json({ status: 'healthy' })
  }),

  // Create game
  http.post(`${API_BASE}/games`, async ({ request }: { request: Request }) => {
    const body = await request.json() as { game_mode: string; template: string; settings?: Record<string, unknown> }
    const game = createGame({
      game_mode: body.game_mode as 'pvp' | 'pvai',
      template: body.template as 'classic' | 'power_chess' | 'leaper_madness' | 'hopper_havoc' | 'pawn_revolution',
      settings: body.settings,
    })
    games.set(game.id, game)
    chatHistory.set(game.id, [createChatMessage({
      message_type: 'system',
      sender_name: 'System',
      content: 'Game created! Share code: ' + game.share_code,
    })])
    return HttpResponse.json(game, { status: 201 })
  }),

  // Get game
  http.get(`${API_BASE}/games/:id`, ({ params }: { params: Record<string, string> }) => {
    const game = games.get(params.id as string)
    if (!game) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 })
    }
    return HttpResponse.json(game)
  }),

  // Join by share code
  http.post(`${API_BASE}/games/join-by-code`, async ({ request }: { request: Request }) => {
    const body = await request.json() as { share_code: string }
    const game = Array.from(games.values()).find(g => g.share_code === body.share_code)
    if (!game) {
      return HttpResponse.json({ detail: 'Invalid share code' }, { status: 404 })
    }
    return HttpResponse.json(game)
  }),

  // Issue command
  http.post(`${API_BASE}/games/:id/command`, async ({ params, request }: { params: Record<string, string>; request: Request }) => {
    const game = games.get(params.id as string)
    if (!game) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 })
    }

    const body = await request.json() as { piece_id: string; target_square: string; message?: string }
    const response: CommandResponse = {
      success: true,
      move_executed: true,
      piece_response: {
        will_move: true,
        response_text: 'I shall advance!',
        morale_before: 70,
        morale_after: 70,
        reason_for_refusal: null,
      },
      board_state: createBoardState({
        last_move: {
          from_square: 'e2',
          to_square: body.target_square,
          san: 'e4',
          piece_type: 'pawn',
        },
      }),
      morale_changes: [],
      analysis: {
        move_quality: 7,
        evaluation: 0.3,
        threats: [],
        opportunities: ['Controls center'],
        analysis_text: 'Good opening move',
      },
      king_taunt: null,
    }

    return HttpResponse.json(response)
  }),

  // Persuade piece
  http.post(`${API_BASE}/games/:id/persuade`, async ({ params }: { params: Record<string, string> }) => {
    const game = games.get(params.id as string)
    if (!game) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 })
    }

    const response: PersuasionResponse = {
      success: true,
      probability: 75,
      piece_response: 'Your words have swayed me. I will make the move.',
      move_executed: true,
      board_state: createBoardState(),
      evaluation: {
        logic_score: 35,
        personality_match: 25,
        morale_modifier: 10,
        trust_modifier: 5,
        urgency_factor: 0,
        total_probability: 75,
      },
    }

    return HttpResponse.json(response)
  }),

  // Resign game
  http.post(`${API_BASE}/games/:id/resign`, ({ params }: { params: Record<string, string> }) => {
    const game = games.get(params.id as string)
    if (!game) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 })
    }
    return HttpResponse.json({ success: true, result: 'black_wins' })
  }),

  // Offer draw
  http.post(`${API_BASE}/games/:id/draw-offer`, ({ params }: { params: Record<string, string> }) => {
    const game = games.get(params.id as string)
    if (!game) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 })
    }
    return HttpResponse.json({ success: true, draw_offered: true })
  }),

  // Respond to draw
  http.post(`${API_BASE}/games/:id/draw-respond`, async ({ params, request }: { params: Record<string, string>; request: Request }) => {
    const game = games.get(params.id as string)
    if (!game) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 })
    }
    const body = await request.json() as { accept: boolean }
    return HttpResponse.json({
      success: true,
      accepted: body.accept,
      result: body.accept ? 'draw' : null,
    })
  }),

  // Get moves
  http.get(`${API_BASE}/games/:id/moves`, ({ params }: { params: Record<string, string> }) => {
    const game = games.get(params.id as string)
    if (!game) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 })
    }
    return HttpResponse.json({
      moves: [],
      total: 0,
    })
  }),

  // Get chat history
  http.get(`${API_BASE}/games/:id/chat`, ({ params, request }: { params: Record<string, string>; request: Request }) => {
    const game = games.get(params.id as string)
    if (!game) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 })
    }

    const url = new URL(request.url)
    const limit = parseInt(url.searchParams.get('limit') ?? '50')
    const offset = parseInt(url.searchParams.get('offset') ?? '0')

    const messages = chatHistory.get(game.id) ?? []
    const paginated = messages.slice(offset, offset + limit)

    return HttpResponse.json({
      items: paginated,
      total: messages.length,
      offset,
      limit,
      has_more: offset + limit < messages.length,
    })
  }),

  // Send chat message
  http.post(`${API_BASE}/games/:id/chat`, async ({ params, request }: { params: Record<string, string>; request: Request }) => {
    const game = games.get(params.id as string)
    if (!game) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 })
    }

    const body = await request.json() as { content: string; message_type?: string }
    const message = createChatMessage({
      message_type: (body.message_type as ChatMessage['message_type']) ?? 'player_message',
      content: body.content,
    })

    const messages = chatHistory.get(game.id) ?? []
    messages.push(message)
    chatHistory.set(game.id, messages)

    return HttpResponse.json(message, { status: 201 })
  }),
]

// Helper to reset the mock store
export function resetMockStore() {
  games.clear()
  chatHistory.clear()
}

// Helper to add a game to the mock store
export function addMockGame(game: Game) {
  games.set(game.id, game)
}

// Helper to get game from mock store
export function getMockGame(id: string): Game | undefined {
  return games.get(id)
}
