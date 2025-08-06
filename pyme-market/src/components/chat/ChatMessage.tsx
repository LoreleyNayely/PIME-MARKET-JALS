interface ChatMessageProps {
  content: string;
  username: string;
  timestamp?: string;
  isCurrentUser: boolean;
}

export function ChatMessage({ content, username, timestamp, isCurrentUser }: ChatMessageProps) {
  const messageTime = timestamp ? new Date(timestamp).toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  }) : '';

  return (
    <div className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[70%] ${isCurrentUser ? 'bg-blue-500 text-white' : 'bg-gray-100'} rounded-lg px-4 py-2`}>
        {!isCurrentUser && (
          <div className="text-xs text-gray-600 font-medium mb-1">
            {username}
          </div>
        )}
        <p className="text-sm whitespace-pre-wrap break-words">
          {content}
        </p>
        {timestamp && (
          <div className={`text-xs mt-1 ${isCurrentUser ? 'text-blue-100' : 'text-gray-500'}`}>
            {messageTime}
          </div>
        )}
      </div>
    </div>
  );
}