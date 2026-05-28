export interface Citation {
  speaker: String;
  party: String;
  topic: String;
  text: String;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

export interface ChatRequest {
  query: string;
  party: string | null;
  provider: 'ollama' | 'openai';
}