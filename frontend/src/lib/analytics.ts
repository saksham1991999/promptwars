/** Google Analytics tracking utilities for Chess Alive */

export const GA_EVENTS = {
    // Game events
    GAME_CREATED: 'game_created',
    GAME_JOINED: 'game_joined',
    GAME_STARTED: 'game_started',
    GAME_COMPLETED: 'game_completed',
    MOVE_MADE: 'move_made',
    PIECE_REFUSED: 'piece_refused',
    PERSUASION_ATTEMPT: 'persuasion_attempt',
    PERSUASION_SUCCESS: 'persuasion_success',

    // Navigation
    PAGE_VIEW: 'page_view',

    // User actions
    CUSTOM_PIECE_CREATED: 'custom_piece_created',
    VOICE_INPUT_USED: 'voice_input_used',
    SHARE_CODE_COPIED: 'share_code_copied',
} as const;

export type GAEventName = (typeof GA_EVENTS)[keyof typeof GA_EVENTS];

interface GAEventParams {
    [key: string]: string | number | boolean | undefined;
}

/** Check if Google Analytics is available */
function isGAAvailable(): boolean {
    return typeof window !== 'undefined' && typeof window.gtag === 'function';
}

/** Track a Google Analytics event */
export function trackGAEvent(eventName: GAEventName, params?: GAEventParams): void {
    if (isGAAvailable()) {
        window.gtag!('event', eventName, params);
    }
}

/** Track a game creation event */
export function trackGameCreated(gameMode: string, template: string): void {
    trackGAEvent(GA_EVENTS.GAME_CREATED, {
        game_mode: gameMode,
        template: template,
    });
}

/** Track when a player joins a game */
export function trackGameJoined(gameMode: string, isShareCode: boolean): void {
    trackGAEvent(GA_EVENTS.GAME_JOINED, {
        game_mode: gameMode,
        via_share_code: isShareCode,
    });
}

/** Track a move with outcome */
export function trackMove(
    pieceType: string,
    wasRefused: boolean,
    requiredPersuasion: boolean
): void {
    trackGAEvent(GA_EVENTS.MOVE_MADE, {
        piece_type: pieceType,
        was_refused: wasRefused,
        required_persuasion: requiredPersuasion,
    });
}

/** Track when a piece refuses a move */
export function trackPieceRefused(pieceType: string, reason: string): void {
    trackGAEvent(GA_EVENTS.PIECE_REFUSED, {
        piece_type: pieceType,
        reason: reason,
    });
}

/** Track persuasion attempt */
export function trackPersuasionAttempt(pieceType: string): void {
    trackGAEvent(GA_EVENTS.PERSUASION_ATTEMPT, {
        piece_type: pieceType,
    });
}

/** Track successful persuasion */
export function trackPersuasionSuccess(pieceType: string, attempts: number): void {
    trackGAEvent(GA_EVENTS.PERSUASION_SUCCESS, {
        piece_type: pieceType,
        attempts: attempts,
    });
}

/** Track custom piece creation */
export function trackCustomPieceCreated(pieceType: string, theme: string): void {
    trackGAEvent(GA_EVENTS.CUSTOM_PIECE_CREATED, {
        piece_type: pieceType,
        theme: theme,
    });
}

/** Track voice input usage */
export function trackVoiceInputUsed(): void {
    trackGAEvent(GA_EVENTS.VOICE_INPUT_USED);
}

/** Track share code copied */
export function trackShareCodeCopied(): void {
    trackGAEvent(GA_EVENTS.SHARE_CODE_COPIED);
}

/** Track game completion */
export function trackGameCompleted(
    result: 'win' | 'loss' | 'draw' | 'resignation',
    totalMoves: number,
    gameMode: string
): void {
    trackGAEvent(GA_EVENTS.GAME_COMPLETED, {
        result: result,
        total_moves: totalMoves,
        game_mode: gameMode,
    });
}

/** Track page view (for SPA navigation) */
export function trackPageView(path: string, title?: string): void {
    if (isGAAvailable()) {
        window.gtag!('event', 'page_view', {
            page_path: path,
            page_title: title || document.title,
            page_location: window.location.href,
        });
    }
}
