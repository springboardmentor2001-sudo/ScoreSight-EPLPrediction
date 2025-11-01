// scoresight/src/services/chatService.ts

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  source?: string;
  confidence?: string;
}

export interface ChatResponse {
  success: boolean;
  question: string;
  response: string;
  source: string;
  confidence: string;
  timestamp: string;
}

export interface Suggestion {
  suggestions: string[];
}

class ChatService {
  private baseUrl = 'http://localhost:8000'; // Your FastAPI backend

  async sendMessage(message: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Chat service error:', error);
      throw new Error('Failed to send message. Please try again.');
    }
  }

  async getSuggestions(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat/suggestions`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: Suggestion = await response.json();
      return data.suggestions;
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
      return [];
    }
  }
}

export const chatService = new ChatService();