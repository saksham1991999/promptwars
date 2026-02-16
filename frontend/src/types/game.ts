/** TypeScript type definitions for Chess Alive game entities */

// ---- Piece & Personality Types ----

export type PieceColor = 'white' | 'black';

export type PieceType =
    | 'pawn' | 'knight' | 'bishop' | 'rook' | 'queen' | 'king'
    | 'chancellor' | 'archbishop' | 'amazon' | 'camel' | 'nightrider'
    | 'grasshopper' | 'cannon' | 'berolina_pawn';

export type MoraleCategory = 'enthusiastic' | 'normal' | 'reluctant' | 'demoralized' | 'mutinous';

export interface PiecePersonality {
    archetype: string;
    traits: string[];
    dialogue_style: string;
    custom_prompt?: string;
    morale_modifiers?: Record<string, number>;
}

export interface GamePiece {
    id: string;
    color: PieceColor;
    piece_type: PieceType;
    square: string | null;
    morale: number;
    personality: PiecePersonality;
    is_captured: boolean;
    is_promoted?: boolean;
    promoted_to?: string;
}

// ---- Game Types ----

export type GameStatus = 'waiting' | 'setup' | 'active' | 'completed' | 'abandoned';
export type GameMode = 'pvp' | 'pvai';
export type GameResult = 'white_wins' | 'black_wins' | 'draw' | 'stalemate' | 'abandoned';
export type TemplateName = 'classic' | 'power_chess' | 'leaper_madness' | 'hopper_havoc' | 'pawn_revolution';

export interface GameSettings {
    surprise_mode: boolean;
    turn_timer: number | null;
    ai_difficulty: 'easy' | 'medium' | 'hard';
}

export interface PlayerSummary {
    id: string;
    username: string;
    avatar_url: string | null;
}

export interface Game {
    id: string;
    status: GameStatus;
    game_mode: GameMode;
    template: TemplateName;
    share_code: string;
    fen: string;
    turn: PieceColor;
    white_player: PlayerSummary | null;
    black_player: PlayerSummary | null;
    pieces: GamePiece[];
    result: GameResult | null;
    settings: GameSettings;
    created_at: string;
}

// ---- Move & Board Types ----

export interface MoveData {
    from_square: string;
    to_square: string;
    san: string;
    piece_type: string;
}

export interface BoardState {
    fen: string;
    turn: string;
    is_check: boolean;
    is_checkmate: boolean;
    is_stalemate: boolean;
    last_move: MoveData | null;
}

export interface MoraleChange {
    piece_id: string;
    event_type: string;
    change: number;
    morale_after: number;
    description: string;
}

// ---- Chat Types ----

export type MessageType =
    | 'player_command' | 'player_message' | 'piece_response' | 'piece_refusal'
    | 'ai_analysis' | 'ai_suggestion' | 'king_taunt' | 'king_reaction'
    | 'system' | 'persuasion_attempt' | 'persuasion_result';

export interface ChatMessage {
    id: string;
    message_type: MessageType;
    sender_id?: string;
    sender_name: string;
    content: string;
    metadata: {
        sending?: boolean;
        [key: string]: any;
    };
    created_at: string;
}

// ---- API Request/Response Types ----

export interface CreateGameRequest {
    game_mode: GameMode;
    template: TemplateName;
    settings?: Partial<GameSettings>;
}

export interface CommandRequest {
    piece_id: string;
    target_square: string;
    message?: string;
}

export interface PersuasionRequest {
    piece_id: string;
    target_square: string;
    argument: string;
    is_voice?: boolean;
}

export interface PieceResponseData {
    will_move: boolean;
    response_text: string;
    morale_before: number;
    morale_after: number;
    reason_for_refusal: string | null;
}

export interface MoveAnalysis {
    move_quality: number;
    evaluation: number;
    threats: string[];
    opportunities: string[];
    analysis_text: string;
}

export interface PersuasionEvaluation {
    logic_score: number;
    personality_match: number;
    morale_modifier: number;
    trust_modifier: number;
    urgency_factor: number;
    total_probability: number;
}

export interface CommandResponse {
    success: boolean;
    move_executed: boolean;
    piece_response: PieceResponseData;
    board_state: BoardState;
    morale_changes: MoraleChange[];
    analysis: MoveAnalysis | null;
    king_taunt: string | null;
}

export interface PersuasionResponse {
    success: boolean;
    probability: number;
    piece_response: string;
    move_executed: boolean;
    board_state: BoardState | null;
    evaluation: PersuasionEvaluation;
}

// ---- User / Profile Types ----

export interface UserProfile {
    id: string;
    username: string;
    email: string;
    avatar_url: string | null;
    games_played: number;
    games_won: number;
    games_lost: number;
    games_drawn: number;
    settings: {
        theme: 'dark' | 'light';
        sound: boolean;
        voice: boolean;
        contrast: boolean;
        motion: boolean;
    };
}

export interface AuthState {
    user: UserProfile | null;
    accessToken: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}
