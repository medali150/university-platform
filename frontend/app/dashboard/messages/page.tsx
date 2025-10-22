'use client'

import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { 
  MessageCircle, 
  Send, 
  Search, 
  Plus, 
  Loader2, 
  User, 
  Check, 
  CheckCheck,
  Paperclip,
  Smile,
  MoreVertical,
  X
} from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import MessagesAPI, { Conversation, Message, UserInfo, MessagesAPIClient } from '@/lib/messages-api'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'

export default function MessagesPage() {
  const { user, loading: authLoading } = useAuth()
  
  // State
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [searchUsers, setSearchUsers] = useState<UserInfo[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [showNewMessageDialog, setShowNewMessageDialog] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load conversations on mount
  useEffect(() => {
    if (user) {
      loadConversations()
    }
  }, [user])

  // Load messages when conversation selected
  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation)
    }
  }, [selectedConversation])

  // Search users for new message
  useEffect(() => {
    if (searchQuery.length >= 2) {
      searchForUsers(searchQuery)
    } else {
      setSearchUsers([])
    }
  }, [searchQuery])

  const loadConversations = async () => {
    try {
      setLoading(true)
      const data = await MessagesAPI.getConversations()
      setConversations(data)
    } catch (error) {
      console.error('Error loading conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadMessages = async (userId: string) => {
    try {
      const data = await MessagesAPI.getConversationMessages(userId)
      setMessages(data)
    } catch (error) {
      console.error('Error loading messages:', error)
    }
  }

  const searchForUsers = async (query: string) => {
    try {
      const data = await MessagesAPI.searchUsers(query)
      setSearchUsers(data)
    } catch (error) {
      console.error('Error searching users:', error)
    }
  }

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return

    try {
      setSending(true)
      await MessagesAPI.sendMessage(selectedConversation, newMessage.trim())
      setNewMessage('')
      await loadMessages(selectedConversation)
      await loadConversations()
    } catch (error) {
      console.error('Error sending message:', error)
      alert('Erreur lors de l\'envoi du message')
    } finally {
      setSending(false)
    }
  }

  const startNewConversation = (userId: string) => {
    setSelectedConversation(userId)
    setShowNewMessageDialog(false)
    setSearchQuery('')
    setSearchUsers([])
  }

  const filteredConversations = conversations.filter(conv =>
    MessagesAPIClient.formatUserName(conv.user).toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const selectedConvData = selectedConversation 
    ? conversations.find(c => c.userId === selectedConversation)
    : null

  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gray-50">
      {/* Sidebar - Conversations List */}
      <div className="w-full md:w-96 bg-white border-r flex flex-col">
        {/* Header */}
        <div className="p-4 border-b bg-white">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold">Messages</h1>
            <Dialog open={showNewMessageDialog} onOpenChange={setShowNewMessageDialog}>
              <DialogTrigger asChild>
                <Button size="sm" className="rounded-full">
                  <Plus className="h-4 w-4" />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Nouveau Message</DialogTitle>
                  <DialogDescription>
                    Recherchez un utilisateur pour démarrer une conversation
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Rechercher par nom ou email..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  {searchUsers.length > 0 && (
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {searchUsers.map((searchUser) => (
                        <div
                          key={searchUser.id}
                          className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                          onClick={() => startNewConversation(searchUser.id)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-lg">
                                {searchUser.prenom.charAt(0)}{searchUser.nom.charAt(0)}
                              </div>
                              <div>
                                <p className="font-medium">{MessagesAPIClient.formatUserName(searchUser)}</p>
                                <p className="text-sm text-muted-foreground">{searchUser.email}</p>
                              </div>
                            </div>
                            <Badge variant="secondary" className={MessagesAPIClient.getRoleBadgeColor(searchUser.role)}>
                              {MessagesAPIClient.getRoleDisplayName(searchUser.role)}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </DialogContent>
            </Dialog>
          </div>
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher une conversation..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 rounded-full bg-gray-100 border-none"
            />
          </div>
        </div>

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto">
          {loading && conversations.length === 0 ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : filteredConversations.length === 0 ? (
            <div className="text-center py-12 px-4 text-muted-foreground">
              <MessageCircle className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <p className="font-medium">Aucune conversation</p>
              <p className="text-sm mt-1">Cliquez sur + pour commencer</p>
            </div>
          ) : (
            filteredConversations.map((conv) => (
              <div
                key={conv.userId}
                className={`p-4 cursor-pointer transition-all hover:bg-gray-50 border-l-4 ${
                  selectedConversation === conv.userId 
                    ? 'bg-blue-50 border-l-blue-500' 
                    : 'border-l-transparent'
                }`}
                onClick={() => setSelectedConversation(conv.userId)}
              >
                <div className="flex items-start space-x-3">
                  {/* Avatar */}
                  <div className="relative flex-shrink-0">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                      {conv.user.prenom.charAt(0)}{conv.user.nom.charAt(0)}
                    </div>
                    {conv.unreadCount > 0 && (
                      <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                        {conv.unreadCount}
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className={`font-semibold truncate ${conv.unreadCount > 0 ? 'text-gray-900' : 'text-gray-700'}`}>
                        {MessagesAPIClient.formatUserName(conv.user)}
                      </h3>
                      <span className="text-xs text-muted-foreground flex-shrink-0 ml-2">
                        {formatDistanceToNow(new Date(conv.lastMessage.createdAt), {
                          addSuffix: false,
                          locale: fr
                        })}
                      </span>
                    </div>
                    <p className={`text-sm truncate ${conv.unreadCount > 0 ? 'font-medium text-gray-900' : 'text-muted-foreground'}`}>
                      {conv.lastMessage.isSent && <Check className="inline h-3 w-3 mr-1" />}
                      {conv.lastMessage.contenu}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white">
        {!selectedConversation ? (
          <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
            <div className="text-center">
              <MessageCircle className="h-24 w-24 mx-auto mb-4 text-gray-300" />
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">Bienvenue dans Messages</h2>
              <p className="text-muted-foreground">
                Sélectionnez une conversation pour commencer à discuter
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b bg-white flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                  {selectedConvData?.user.prenom.charAt(0)}{selectedConvData?.user.nom.charAt(0)}
                </div>
                <div>
                  <h2 className="font-semibold">{selectedConvData && MessagesAPIClient.formatUserName(selectedConvData.user)}</h2>
                  <p className="text-xs text-muted-foreground">
                    {selectedConvData && MessagesAPIClient.getRoleDisplayName(selectedConvData.user.role)}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="sm">
                <MoreVertical className="h-5 w-5" />
              </Button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-br from-gray-50 to-gray-100">
              {messages.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <p>Aucun message</p>
                  <p className="text-sm mt-1">Envoyez le premier message!</p>
                </div>
              ) : (
                messages.map((msg, index) => {
                  const isSent = msg.id_expediteur === user?.id
                  const showAvatar = index === 0 || messages[index - 1].id_expediteur !== msg.id_expediteur

                  return (
                    <div
                      key={msg.id}
                      className={`flex ${isSent ? 'justify-end' : 'justify-start'} items-end space-x-2`}
                    >
                      {!isSent && showAvatar && (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white text-xs font-semibold">
                          {msg.expediteur.prenom.charAt(0)}
                        </div>
                      )}
                      {!isSent && !showAvatar && <div className="w-8" />}

                      <div className={`max-w-[70%] ${isSent ? 'order-2' : 'order-1'}`}>
                        <div
                          className={`rounded-2xl px-4 py-2 ${
                            isSent
                              ? 'bg-blue-500 text-white rounded-br-md'
                              : 'bg-white text-gray-900 rounded-bl-md shadow-sm'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap break-words">{msg.contenu}</p>
                        </div>
                        <div className={`flex items-center space-x-1 mt-1 px-2 ${isSent ? 'justify-end' : 'justify-start'}`}>
                          <span className="text-xs text-muted-foreground">
                            {new Date(msg.createdAt).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                          {isSent && (
                            <CheckCheck className="h-3 w-3 text-blue-500" />
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t bg-white">
              <div className="flex items-end space-x-2">
                <Button variant="ghost" size="sm" className="rounded-full">
                  <Smile className="h-5 w-5 text-gray-500" />
                </Button>
                <Button variant="ghost" size="sm" className="rounded-full">
                  <Paperclip className="h-5 w-5 text-gray-500" />
                </Button>
                <Textarea
                  placeholder="Tapez un message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      sendMessage()
                    }
                  }}
                  rows={1}
                  className="flex-1 resize-none rounded-full border-gray-300 focus:border-blue-500 py-3"
                />
                <Button 
                  onClick={sendMessage} 
                  disabled={!newMessage.trim() || sending}
                  className="rounded-full w-12 h-12 p-0"
                >
                  {sending ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
