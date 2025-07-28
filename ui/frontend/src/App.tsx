import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { 
  Send, 
  Plus, 
  Trash2, 
  Menu, 
  X, 
  Download,
  FileText,
  Search,
  Loader2
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Chat {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: string;
  chat_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  report_path?: string;
}

interface AGUIMessage {
  type: string;
  text?: string;
  sender?: string;
  event?: string;
  data?: any;
}

interface AGUIState {
  current_query: string;
  is_researching: boolean;
  research_status: string;
  chat_id: string;
  notes: string[];
  final_report: string;
}

const App: React.FC = () => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [agentState, setAgentState] = useState<AGUIState>({
    current_query: '',
    is_researching: false,
    research_status: '',
    chat_id: '',
    notes: [],
    final_report: ''
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('Connected to AG-UI server');
      setIsLoading(false);
    };
    
    ws.onmessage = (event) => {
      const message: AGUIMessage = JSON.parse(event.data);
      console.log('AG-UI message:', message);
      
      if (message.type === 'message' && message.sender === 'assistant') {
        // Add assistant message to UI only if it's for the current chat
        const chatId = agentState.chat_id || currentChatId || '';
        if (chatId && (chatId === currentChatId || !currentChatId)) {
          const newMessage: Message = {
            id: Date.now().toString(),
            chat_id: chatId,
            role: 'assistant',
            content: message.text || '',
            timestamp: new Date().toISOString()
          };
          setMessages(prev => [...prev, newMessage]);
        }
        setIsLoading(false);
      } else if (message.type === 'event') {
        // Handle custom events
        if (message.event === 'research_started') {
          setIsLoading(true);
        } else if (message.event === 'research_completed') {
          setIsLoading(false);
          // Reload messages to get the saved version
          if (currentChatId) {
            loadMessages(currentChatId);
          }
        } else if (message.event === 'research_progress') {
          // Update progress (could add a progress bar)
          console.log('Progress:', message.data);
        }
      } else if (message.type === 'state') {
        // Update agent state
        const stateData = message.data as AGUIState;
        setAgentState(stateData);
        
        // Update current chat ID if provided
        if (stateData.chat_id) {
          if (!currentChatId || currentChatId !== stateData.chat_id) {
            setCurrentChatId(stateData.chat_id);
            loadChats();
          }
        }
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, 3000);
    };
    
    wsRef.current = ws;
  };

  // Load chats on mount
  useEffect(() => {
    loadChats();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChats = async () => {
    try {
      const response = await axios.get('/api/chats');
      setChats(response.data);
    } catch (error) {
      console.error('Error loading chats:', error);
    }
  };

  const loadMessages = async (chatId: string) => {
    try {
      const response = await axios.get(`/api/chats/${chatId}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const createNewChat = async () => {
    try {
      const response = await axios.post('/api/chats', {
        title: 'New Research'
      });
      await loadChats();
      setCurrentChatId(response.data.id);
      setMessages([]);
      setAgentState(prev => ({ ...prev, chat_id: response.data.id }));
      return response.data;
    } catch (error) {
      console.error('Error creating chat:', error);
      return null;
    }
  };

  const deleteChat = async (chatId: string) => {
    try {
      await axios.delete(`/api/chats/${chatId}`);
      await loadChats();
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setMessages([]);
        setAgentState({
          current_query: '',
          is_researching: false,
          research_status: '',
          chat_id: '',
          notes: [],
          final_report: ''
        });
      }
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  };

  const selectChat = async (chatId: string) => {
    setCurrentChatId(chatId);
    await loadMessages(chatId);
    setAgentState(prev => ({ ...prev, chat_id: chatId }));
    
    // Notify backend of chat selection
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'select_chat',
        chat_id: chatId
      }));
    }
  };

  const sendMessageToAgent = (text: string, chatId?: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = {
        type: 'message',
        text: text,
        sender: 'user',
        chat_id: chatId || currentChatId
      };
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket not connected');
      // Try to reconnect
      connectWebSocket();
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsLoading(true);

    let chatId = currentChatId;

    // Create new chat if needed
    if (!chatId) {
      const response = await createNewChat();
      if (response && response.id) {
        chatId = response.id;
        setCurrentChatId(chatId);
      }
    }

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: Date.now().toString(),
      chat_id: chatId || '',
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMessage]);

    // Send message via AG-UI WebSocket with chat_id
    sendMessageToAgent(userMessage, chatId);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return format(new Date(timestamp), 'MMM d, yyyy h:mm a');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-gray-900 text-white overflow-hidden flex flex-col`}>
        <div className="p-4 border-b border-gray-800">
          <button
            onClick={createNewChat}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
          >
            <Plus size={20} />
            New Research
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`p-3 hover:bg-gray-800 cursor-pointer flex items-center justify-between group ${
                currentChatId === chat.id ? 'bg-gray-800' : ''
              }`}
              onClick={() => selectChat(chat.id)}
            >
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <FileText size={16} className="flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{chat.title}</div>
                  <div className="text-xs text-gray-400">
                    {format(new Date(chat.updated_at), 'MMM d, yyyy')}
                  </div>
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteChat(chat.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-700 rounded transition-opacity"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h1 className="text-xl font-semibold">Open Deep Research</h1>
          </div>
          
          {agentState.is_researching && (
            <div className="flex items-center gap-2 text-blue-600">
              <Loader2 size={20} className="animate-spin" />
              <span className="text-sm">{agentState.research_status}</span>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 && !currentChatId ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <Search size={48} className="mb-4" />
              <h2 className="text-2xl font-semibold mb-2">Start a New Research</h2>
              <p className="text-center max-w-md">
                Ask me anything and I'll conduct deep research to provide you with comprehensive insights and analysis.
              </p>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`mb-6 ${message.role === 'user' ? 'text-right' : 'text-left'}`}
                >
                  <div className={`inline-block max-w-full ${
                    message.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-2xl px-4 py-2'
                      : 'bg-white border border-gray-200 rounded-2xl p-4'
                  }`}>
                    {message.role === 'user' ? (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    ) : (
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown
                          components={{
                            code: ({ inline, className, children, ...props }) => {
                              return !inline ? (
                                <pre className="bg-gray-100 rounded-lg p-3 overflow-x-auto">
                                  <code className={className} {...props}>
                                    {children}
                                  </code>
                                </pre>
                              ) : (
                                <code className="bg-gray-100 rounded px-1 py-0.5" {...props}>
                                  {children}
                                </code>
                              );
                            }
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                        
                        {message.report_path && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <a
                              href={`/api/reports/${message.report_path.split('/').pop()}`}
                              download
                              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm"
                            >
                              <Download size={16} />
                              Download Report
                            </a>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {formatTimestamp(message.timestamp)}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="mb-6">
                  <div className="inline-block bg-white border border-gray-200 rounded-2xl p-4">
                    <div className="flex items-center gap-2">
                      <Loader2 size={20} className="animate-spin text-blue-600" />
                      <span className="text-gray-600">Researching...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything for deep research..."
                className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[50px] max-h-[200px]"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;