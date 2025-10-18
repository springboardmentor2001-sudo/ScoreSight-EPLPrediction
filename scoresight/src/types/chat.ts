export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export interface QuickQuestion {
  id: string;
  question: string;
  category: string;
}