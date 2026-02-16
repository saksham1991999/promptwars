/** API service layer — axios HTTP client with session-based auth */
import axios, { type AxiosInstance } from 'axios';
import type {
    Game,
    CreateGameRequest,
    CommandRequest,
    CommandResponse,
    PersuasionRequest,
    PersuasionResponse,
    ChatMessage,
} from '../types/game';

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!BASE_URL) {
    throw new Error('VITE_API_BASE_URL environment variable is not configured');
}

/** Get or create a session ID stored in localStorage */
export function getSessionId(): string {
    let id = localStorage.getItem('chessalive_session_id');
    if (!id) {
        id = crypto.randomUUID();
        localStorage.setItem('chessalive_session_id', id);
    }
    return id;
}

class ApiService {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: BASE_URL,
            headers: { 'Content-Type': 'application/json' },
            timeout: 15000,
        });

        // Attach session ID to every request
        this.client.interceptors.request.use((config) => {
            config.headers['X-Session-Id'] = getSessionId();
            return config;
        });
    }

    // --- Games ---
    async createGame(data: CreateGameRequest): Promise<Game> {
        const res = await this.client.post<Game>('/games', data);
        return res.data;
    }

    async getGame(gameId: string): Promise<Game> {
        const res = await this.client.get<Game>(`/games/${gameId}`);
        return res.data;
    }

    async joinByShareCode(shareCode: string): Promise<Game> {
        const res = await this.client.post<Game>('/games/join-by-code', { share_code: shareCode });
        return res.data;
    }

    async issueCommand(gameId: string, data: CommandRequest): Promise<CommandResponse> {
        const res = await this.client.post<CommandResponse>(`/games/${gameId}/command`, data);
        return res.data;
    }

    async persuade(gameId: string, data: PersuasionRequest): Promise<PersuasionResponse> {
        const res = await this.client.post<PersuasionResponse>(`/games/${gameId}/persuade`, data);
        return res.data;
    }

    async resign(gameId: string): Promise<{ success: boolean; result: string }> {
        const res = await this.client.post(`/games/${gameId}/resign`);
        return res.data;
    }

    async offerDraw(gameId: string): Promise<{ success: boolean }> {
        const res = await this.client.post(`/games/${gameId}/draw-offer`);
        return res.data;
    }

    async respondToDraw(gameId: string, accept: boolean): Promise<{ success: boolean; result: string }> {
        const res = await this.client.post(`/games/${gameId}/draw-respond`, { accept });
        return res.data;
    }

    async getMoves(gameId: string): Promise<{ moves: unknown[] }> {
        const res = await this.client.get(`/games/${gameId}/moves`);
        return res.data;
    }

    // --- Chat ---
    async getChatHistory(gameId: string, page = 1, pageSize = 50) {
        const res = await this.client.get<{
            data: ChatMessage[];
            total: number;
            page: number;
            has_more: boolean;
        }>(`/games/${gameId}/chat`, { params: { page, page_size: pageSize } });
        return res.data;
    }

    async sendChatMessage(gameId: string, content: string, messageType = 'player_message') {
        const res = await this.client.post<ChatMessage>(`/games/${gameId}/chat`, { content, message_type: messageType });
        return res.data;
    }
}

export const api = new ApiService();
