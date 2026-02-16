import type {
  Game,
  GameStatus,
  GameMode,
  TemplateName,
  GameResult,
  GameSettings,
  BoardState,
  MoveData,
  PlayerSummary,
} from '../../types/game'
import { createPieces, type PieceOverrides } from './piece'

const STANDARD_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

interface GameOverrides {
  id?: string
  status?: GameStatus
  game_mode?: GameMode
  template?: TemplateName
  share_code?: string
  fen?: string
  turn?: 'white' | 'black'
  white_player?: PlayerSummary | null
  black_player?: PlayerSummary | null
  pieces?: PieceOverrides[]
  result?: GameResult | null
  settings?: Partial<GameSettings>
  created_at?: string
}

export const createGame = (overrides: GameOverrides = {}): Game => {
  const id = overrides.id ?? `game-${Math.random().toString(36).substr(2, 9)}`
  const gameMode = overrides.game_mode ?? 'pvp'
  const turn = overrides.turn ?? 'white'

  const whitePlayer: PlayerSummary | null =
    overrides.white_player !== undefined
      ? overrides.white_player
      : gameMode === 'pvp'
        ? { id: 'player-white', username: 'White Player', avatar_url: null }
        : null

  const blackPlayer: PlayerSummary | null =
    overrides.black_player !== undefined
      ? overrides.black_player
      : gameMode === 'pvp'
        ? { id: 'player-black', username: 'Black Player', avatar_url: null }
        : { id: 'ai', username: 'AI Opponent', avatar_url: null }

  return {
    id,
    status: overrides.status ?? 'active',
    game_mode: gameMode,
    template: overrides.template ?? 'classic',
    share_code: overrides.share_code ?? Math.random().toString(36).substr(2, 8).toUpperCase(),
    fen: overrides.fen ?? STANDARD_FEN,
    turn,
    white_player: whitePlayer,
    black_player: blackPlayer,
    pieces: createPieces(overrides.pieces),
    result: overrides.result ?? null,
    settings: {
      surprise_mode: false,
      turn_timer: null,
      ai_difficulty: 'medium',
      ...overrides.settings,
    },
    created_at: overrides.created_at ?? new Date().toISOString(),
  }
}

export const createBoardState = (overrides: Partial<BoardState> = {}): BoardState => ({
  fen: overrides.fen ?? STANDARD_FEN,
  turn: overrides.turn ?? 'white',
  is_check: overrides.is_check ?? false,
  is_checkmate: overrides.is_checkmate ?? false,
  is_stalemate: overrides.is_stalemate ?? false,
  last_move: overrides.last_move ?? null,
})

export const createMoveData = (overrides: Partial<MoveData> = {}): MoveData => ({
  from_square: overrides.from_square ?? 'e2',
  to_square: overrides.to_square ?? 'e4',
  san: overrides.san ?? 'e4',
  piece_type: overrides.piece_type ?? 'pawn',
})

export const createPlayerSummary = (overrides: Partial<PlayerSummary> = {}): PlayerSummary => ({
  id: overrides.id ?? `player-${Math.random().toString(36).substr(2, 9)}`,
  username: overrides.username ?? 'Test Player',
  avatar_url: overrides.avatar_url ?? null,
})
