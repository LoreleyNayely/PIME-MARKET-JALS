import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { chatService } from '../../services/chatService';
import { ChatMessage } from './ChatMessage';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { UsersIcon } from '@heroicons/react/24/outline';

interface Message {
  messageId?: string;
  content: string;
  username: string;
  timestamp?: string;
}

export function ChatContainer() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [usersOnline, setUsersOnline] = useState<string[]>([]);
  const [showUsers, setShowUsers] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    
    if (user?.name) {
      chatService.connect(user.name);

      const unsubscribe = chatService.onMessage((data) => {
        switch (data.type) {
          case 'message':
            if (data.content && data.username) {
              const newMessage: Message = {
                content: data.content,
                username: data.username,
                timestamp: new Date().toISOString()
              };
              setMessages(prev => [...prev, newMessage]);
            }
            break;
          case 'history':
            if (data.messages) {
              setMessages(data.messages);
            }
            break;
          case 'users_online':
            if (data.users_online) {
              setUsersOnline(data.users_online);
            }
            break;
          case 'user_left':
            if (data.users_online) {
              setUsersOnline(data.users_online);
            }
            break;
        }
      });

      const unsubscribeConnection = chatService.onConnectionChange((status) => {
        setIsConnected(status);
      });

      return () => {
        unsubscribe();
        unsubscribeConnection();
        chatService.disconnect();
      };
    }
  }, [user?.name]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMessage.trim() && isConnected) {
      chatService.sendMessage(newMessage.trim());
      setNewMessage('');
    }
  };

  const toggleUsersList = () => {
    setShowUsers(!showUsers);
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-600">Debes iniciar sesión para usar el chat</p>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-8rem)]">
      <Card className="flex-1 flex flex-col overflow-hidden">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            Chat General
          </h2>
          <Button
            variant="ghost"
            onClick={toggleUsersList}
            className="flex items-center gap-2"
          >
            <UsersIcon className="h-5 w-5" />
            <span className="text-sm">
              {usersOnline.length} en línea
            </span>
          </Button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4">
            {messages.map((message, index) => (
              <ChatMessage
                key={message.messageId || index}
                content={message.content}
                username={message.username}
                timestamp={message.timestamp}
                isCurrentUser={message.username === user?.name}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>

          {showUsers && (
            <div className="w-64 border-l overflow-y-auto p-4 bg-gray-50">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Usuarios en línea
              </h3>
              <ul className="space-y-2">
                {usersOnline.map(username => (
                  <li
                    key={username}
                    className="text-sm text-gray-600 flex items-center gap-2"
                  >
                    <span className="w-2 h-2 bg-green-500 rounded-full" />
                    {username}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t">
          <div className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Escribe un mensaje..."
              className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={!isConnected}
            />
            <Button
              type="submit"
              disabled={!isConnected || !newMessage.trim()}
              className="px-6"
            >
              Enviar
            </Button>
          </div>
          {!isConnected && (
            <p className="text-sm text-red-500 mt-2">
            </p>
          )}
        </form>
      </Card>
    </div>
  );
}