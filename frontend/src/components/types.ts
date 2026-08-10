export interface Message {
  id : string,
  conversation_id: string | null;
  text: string;
  sender: 'user' | 'ai';
  title?: string | null;
}

export interface RecentChat {
  id: string;
  title: string;
  updatedAt: number;
}