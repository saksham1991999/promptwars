import type { GamePiece, PieceColor, PieceType, PiecePersonality, MoraleCategory } from '../../types/game'

const STANDARD_PIECE_SETUP: Array<{ type: PieceType; color: PieceColor; square: string }> = [
  // White pieces
  { type: 'rook', color: 'white', square: 'a1' },
  { type: 'knight', color: 'white', square: 'b1' },
  { type: 'bishop', color: 'white', square: 'c1' },
  { type: 'queen', color: 'white', square: 'd1' },
  { type: 'king', color: 'white', square: 'e1' },
  { type: 'bishop', color: 'white', square: 'f1' },
  { type: 'knight', color: 'white', square: 'g1' },
  { type: 'rook', color: 'white', square: 'h1' },
  // White pawns
  ...Array.from({ length: 8 }, (_, i) => ({
    type: 'pawn' as PieceType,
    color: 'white' as PieceColor,
    square: `${String.fromCharCode(97 + i)}2`,
  })),
  // Black pawns
  ...Array.from({ length: 8 }, (_, i) => ({
    type: 'pawn' as PieceType,
    color: 'black' as PieceColor,
    square: `${String.fromCharCode(97 + i)}7`,
  })),
  // Black pieces
  { type: 'rook', color: 'black', square: 'a8' },
  { type: 'knight', color: 'black', square: 'b8' },
  { type: 'bishop', color: 'black', square: 'c8' },
  { type: 'queen', color: 'black', square: 'd8' },
  { type: 'king', color: 'black', square: 'e8' },
  { type: 'bishop', color: 'black', square: 'f8' },
  { type: 'knight', color: 'black', square: 'g8' },
  { type: 'rook', color: 'black', square: 'h8' },
]

const PERSONALITY_ARCHETYPES: Record<PieceType, string[]> = {
  pawn: ['loyal_soldier', 'reluctant_fighter', 'ambitious_grunt'],
  knight: ['daring_hero', 'lone_wolf', 'chivalrous_guardian'],
  bishop: ['wise_counselor', 'devoted_mystic', 'calculating_strategist'],
  rook: ['steadfast_defender', 'siege_master', 'unyielding_fortress'],
  queen: ['ruthless_conqueror', 'noble_protector', 'ambitious_ruler'],
  king: ['cautious_monarch', 'inspiring_leader', 'paranoid_ruler'],
  chancellor: ['tactical_genius', 'field_commander'],
  archbishop: ['holy_warrior', 'divine_tactician'],
  amazon: ['fearless_warrior', 'legendary_champion'],
  camel: ['desert_wanderer', 'enduring_traveler'],
  nightrider: ['shadow_striker', 'midnight_raider'],
  grasshopper: ['unconventional_tactician', 'surprise_attacker'],
  cannon: ['artillery_expert', 'long_range_specialist'],
  berolina_pawn: ['cunning_infiltrator', 'unpredictable_fighter'],
}

export interface PieceOverrides {
  id?: string
  color?: PieceColor
  piece_type?: PieceType
  square?: string | null
  morale?: number
  personality?: Partial<PiecePersonality>
  is_captured?: boolean
  is_promoted?: boolean
  promoted_to?: string
}

export const createPersonality = (
  pieceType: PieceType,
  overrides: Partial<PiecePersonality> = {}
): PiecePersonality => {
  const archetypes = PERSONALITY_ARCHETYPES[pieceType] ?? ['neutral']
  const archetype = overrides.archetype ?? archetypes[0]

  return {
    archetype,
    traits: overrides.traits ?? ['brave', 'loyal'],
    dialogue_style: overrides.dialogue_style ?? 'formal',
    custom_prompt: overrides.custom_prompt,
    morale_modifiers: overrides.morale_modifiers ?? {},
  }
}

export const createPiece = (overrides: PieceOverrides = {}): GamePiece => {
  const pieceType = overrides.piece_type ?? 'pawn'
  const color = overrides.color ?? 'white'

  return {
    id: overrides.id ?? `piece-${Math.random().toString(36).substr(2, 9)}`,
    color,
    piece_type: pieceType,
    square: overrides.square ?? null,
    morale: overrides.morale ?? 70,
    personality: createPersonality(pieceType, overrides.personality),
    is_captured: overrides.is_captured ?? false,
    is_promoted: overrides.is_promoted ?? false,
    promoted_to: overrides.promoted_to,
  }
}

export const createPieces = (overrides: PieceOverrides[] = []): GamePiece[] => {
  if (overrides.length > 0) {
    return overrides.map((pieceOverride, index) =>
      createPiece({
        ...STANDARD_PIECE_SETUP[index],
        ...pieceOverride,
      })
    )
  }

  return STANDARD_PIECE_SETUP.map((setup, index) =>
    createPiece({
      id: `piece-${index}`,
      type: setup.type,
      color: setup.color,
      square: setup.square,
    })
  )
}

export const getMoraleCategory = (morale: number): MoraleCategory => {
  if (morale >= 80) return 'enthusiastic'
  if (morale >= 60) return 'normal'
  if (morale >= 40) return 'reluctant'
  if (morale >= 20) return 'demoralized'
  return 'mutinous'
}
