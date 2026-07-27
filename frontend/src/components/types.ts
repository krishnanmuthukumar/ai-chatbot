export interface Message {
  id : string,    
  conversation_id: string | null;            
  text: string;
  sender: 'user' | 'ai';   
}