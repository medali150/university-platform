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
  const [availableContacts, setAvailableContacts] = useState<UserInfo[]>([])
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [searchUsers, setSearchUsers] = useState<UserInfo[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [showNewMessageDialog, setShowNewMessageDialog] = useState(false)
  const [showAllContacts, setShowAllContacts] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load conversations and available contacts on mount
  useEffect(() => {
    if (user) {
      loadConversations()
      loadAvailableContacts()
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
      console.log('💬 Loading conversations...')
      const data = await MessagesAPI.getConversations()
      console.log(`✅ Loaded ${data.length} conversations:`, data)
      setConversations(data)
    } catch (error) {
      console.error('❌ Error loading conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadAvailableContacts = async () => {
    try {
      console.log('📞 Loading available contacts...')
      const data = await MessagesAPI.getAvailableContacts()
      console.log(`✅ Loaded ${data.length} contacts:`, data)
      setAvailableContacts(data)
    } catch (error) {
      console.error('❌ Error loading contacts:', error)
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

  // Combine conversations and available contacts
  const allContacts = () => {
    const contactsMap = new Map<string, any>()
    
    // Add existing conversations first
    conversations.forEach(conv => {
      contactsMap.set(conv.userId, {
        userId: conv.userId,
        user: conv.user,
        lastMessage: conv.lastMessage,
        unreadCount: conv.unreadCount,
        hasConversation: true
      })
    })
    
    // Add available contacts who don't have conversations yet
    availableContacts.forEach(contact => {
      if (!contactsMap.has(contact.id)) {
        contactsMap.set(contact.id, {
          userId: contact.id,
          user: contact,
          lastMessage: null,
          unreadCount: 0,
          hasConversation: false
        })
      }
    })
    
    return Array.from(contactsMap.values())
  }

  const filteredContacts = allContacts().filter(contact =>
    MessagesAPIClient.formatUserName(contact.user).toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.user.email.toLowerCase().includes(searchTerm.toLowerCase())
  ).sort((a, b) => {
    // Sort: conversations first, then by last message time or alphabetically
    if (a.hasConversation && !b.hasConversation) return -1
    if (!a.hasConversation && b.hasConversation) return 1
    
    if (a.lastMessage && b.lastMessage) {
      return new Date(b.lastMessage.createdAt).getTime() - new Date(a.lastMessage.createdAt).getTime()
    }
    
    if (a.lastMessage && !b.lastMessage) return -1
    if (!a.lastMessage && b.lastMessage) return 1
    
    // Alphabetical by name
    return MessagesAPIClient.formatUserName(a.user).localeCompare(MessagesAPIClient.formatUserName(b.user))
  })

  const selectedConvData = selectedConversation 
    ? filteredContacts.find(c => c.userId === selectedConversation)
    : null

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <p className="text-white/60">Chargement des messages...</p>
        </div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="space-y-6 p-4 sm:p-6 md:p-8">
      {/* Header Section - Matching Dashboard Style */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-6 sm:p-8 text-white shadow-lg">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <MessageCircle className="h-8 w-8" />
            <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">Messages 💬</h1>
          </div>
          <p className="text-blue-100 text-base sm:text-lg">
            Communiquez avec vos enseignants et étudiants
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-16rem)] bg-white rounded-lg shadow-lg overflow-hidden border-0">
        {/* Sidebar - Conversations List */}
        <div className="w-full md:w-96 border-r flex flex-col bg-gradient-to-br from-gray-50 to-white">
          {/* Header */}
          <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-cyan-50">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">Conversations</h2>
            <Dialog open={showNewMessageDialog} onOpenChange={setShowNewMessageDialog}>
              <DialogTrigger asChild>
                <Button size="sm" className="rounded-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-md">
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
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Rechercher une conversation..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 rounded-lg bg-white border-gray-200 shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Contacts List */}
        <div className="flex-1 overflow-y-auto">
          {loading && conversations.length === 0 && availableContacts.length === 0 ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : filteredContacts.length === 0 ? (
            <div className="text-center py-12 px-4 text-muted-foreground">
              <MessageCircle className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <p className="font-medium">Aucun contact</p>
              <p className="text-sm mt-1">Aucun contact disponible</p>
            </div>
          ) : (
            filteredContacts.map((contact) => (
              <div
                key={contact.userId}
                className={`p-4 cursor-pointer transition-all duration-200 border-l-4 ${
                  selectedConversation === contact.userId 
                    ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-l-blue-500 shadow-sm' 
                    : 'border-l-transparent hover:bg-gray-50'
                }`}
                onClick={() => setSelectedConversation(contact.userId)}
              >
                <div className="flex items-start space-x-3">
                  {/* Avatar */}
                  <div className="relative flex-shrink-0">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold shadow-md">
                      {contact.user.prenom.charAt(0)}{contact.user.nom.charAt(0)}
                    </div>
                    {contact.unreadCount > 0 && (
                      <div className="absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-br from-red-500 to-pink-600 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-lg animate-pulse">
                        {contact.unreadCount}
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className={`font-semibold truncate ${contact.unreadCount > 0 ? 'text-gray-900' : 'text-gray-700'}`}>
                        {MessagesAPIClient.formatUserName(contact.user)}
                      </h3>
                      {contact.lastMessage && (
                        <span className="text-xs text-muted-foreground flex-shrink-0 ml-2">
                          {formatDistanceToNow(new Date(contact.lastMessage.createdAt), {
                            addSuffix: false,
                            locale: fr
                          })}
                        </span>
                      )}
                    </div>
                    {contact.lastMessage ? (
                      <p className={`text-sm truncate ${contact.unreadCount > 0 ? 'font-medium text-gray-900' : 'text-muted-foreground'}`}>
                        {contact.lastMessage.isSent && <Check className="inline h-3 w-3 mr-1" />}
                        {contact.lastMessage.contenu}
                      </p>
                    ) : (
                      <p className="text-sm text-muted-foreground italic">
                        <Badge variant="secondary" className={MessagesAPIClient.getRoleBadgeColor(contact.user.role)}>
                          {MessagesAPIClient.getRoleDisplayName(contact.user.role)}
                        </Badge>
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {!selectedConversation ? (
          <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
            <div className="text-center p-8 rounded-2xl bg-white/80 backdrop-blur-sm shadow-xl border border-white/20">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                <MessageCircle className="h-12 w-12 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Bienvenue dans Messages</h2>
              <p className="text-gray-600">
                Sélectionnez une conversation pour commencer à discuter
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-cyan-50 flex items-center justify-between shadow-sm">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold shadow-md">
                  {selectedConvData?.user.prenom.charAt(0)}{selectedConvData?.user.nom.charAt(0)}
                </div>
                <div>
                  <h2 className="font-bold text-gray-800">{selectedConvData && MessagesAPIClient.formatUserName(selectedConvData.user)}</h2>
                  <p className="text-xs text-gray-600">
                    {selectedConvData && MessagesAPIClient.getRoleDisplayName(selectedConvData.user.role)}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="sm" className="hover:bg-white/50">
                <MoreVertical className="h-5 w-5 text-gray-600" />
              </Button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-br from-blue-50/30 via-purple-50/30 to-pink-50/30">
              {messages.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                    <MessageCircle className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="font-medium">Aucun message</p>
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
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white text-xs font-semibold shadow-md">
                          {msg.expediteur.prenom.charAt(0)}
                        </div>
                      )}
                      {!isSent && !showAvatar && <div className="w-8" />}

                      <div className={`max-w-[70%] ${isSent ? 'order-2' : 'order-1'}`}>
                        <div
                          className={`rounded-2xl px-4 py-3 ${
                            isSent
                              ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-br-md shadow-md'
                              : 'bg-white text-gray-900 rounded-bl-md shadow-md border border-gray-100'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap break-words">{msg.contenu}</p>
                        </div>
                        <div className={`flex items-center space-x-1 mt-1 px-2 ${isSent ? 'justify-end' : 'justify-start'}`}>
                          <span className="text-xs text-gray-500">
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
            <div className="p-4 border-t bg-gradient-to-r from-blue-50 to-cyan-50 shadow-lg">
              <div className="flex items-end space-x-2 bg-white rounded-2xl p-2 shadow-md">
                <Button variant="ghost" size="sm" className="rounded-full hover:bg-blue-50">
                  <Smile className="h-5 w-5 text-gray-500" />
                </Button>
                <Button variant="ghost" size="sm" className="rounded-full hover:bg-blue-50">
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
                  className="flex-1 resize-none border-none focus:ring-0 py-3 bg-transparent"
                />
                <Button 
                  onClick={sendMessage} 
                  disabled={!newMessage.trim() || sending}
                  className="rounded-full w-12 h-12 p-0 bg-gradient-to-br from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 shadow-lg"
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
    </div>
  )
}
