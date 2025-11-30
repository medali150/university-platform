'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { classroomApi } from '@/lib/classroom-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  ArrowLeft, 
  Send, 
  Bot, 
  User,
  Sparkles,
  BookOpen,
  Lightbulb,
  Target,
  Copy,
  CheckCircle2,
  RefreshCw,
  Trash2,
  MessageSquare,
  Brain,
  Zap,
  Home
} from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isError?: boolean;
}

export default function AIAssistantPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "👋 **Bonjour!** Je suis votre **Assistant IA d'Apprentissage** propulsé par Groq.\n\n🎓 Je peux vous aider avec:\n- Explications de concepts complexes\n- Résolution de problèmes\n- Préparation aux examens\n- Création de résumés\n- Génération d'exercices\n- Conseils d'étude personnalisés\n\n💡 **Astuce:** Sélectionnez un cours dans le menu à gauche pour obtenir des réponses spécifiques à votre programme!\n\nComment puis-je vous aider aujourd'hui?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [courses, setCourses] = useState<any[]>([]);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    loadCourses();
    // Focus input on mount
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadCourses = async () => {
    try {
      const data = await classroomApi.getCourses();
      setCourses(data);
    } catch (error) {
      console.error('Failed to load courses:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const copyToClipboard = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(messageId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const clearConversation = () => {
    if (confirm('Êtes-vous sûr de vouloir effacer toute la conversation?')) {
      setMessages([{
        id: Date.now().toString(),
        role: 'assistant',
        content: "Conversation effacée. Comment puis-je vous aider?",
        timestamp: new Date()
      }]);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput('');
    setLoading(true);

    try {
      const response = await classroomApi.chatWithAI(
        currentInput,
        undefined,
        selectedCourse || undefined
      );

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "❌ Désolé, je rencontre un problème technique. Veuillez réessayer dans un moment.",
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      // Refocus input after sending
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const regenerateResponse = async (userMessageIndex: number) => {
    const userMessage = messages[userMessageIndex];
    if (!userMessage || userMessage.role !== 'user') return;

    setLoading(true);
    
    // Remove the previous response
    setMessages(prev => prev.slice(0, userMessageIndex + 1));

    try {
      const response = await classroomApi.chatWithAI(
        userMessage.content,
        undefined,
        selectedCourse || undefined
      );

      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to regenerate:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    {
      icon: Brain,
      title: "Explications",
      prompts: [
        "Explique-moi ce concept en termes simples",
        "Quelles sont les idées principales à retenir?",
        "Comment est-ce lié aux autres concepts?"
      ]
    },
    {
      icon: Lightbulb,
      title: "Exemples",
      prompts: [
        "Donne-moi des exemples concrets",
        "Montre-moi une application pratique",
        "Crée un exercice pour pratiquer"
      ]
    },
    {
      icon: Target,
      title: "Étude",
      prompts: [
        "Quelles sont les meilleures stratégies d'étude?",
        "Crée un plan de révision",
        "Quels sont les points difficiles?"
      ]
    },
    {
      icon: Sparkles,
      title: "Révision",
      prompts: [
        "Résume les points clés",
        "Crée des flashcards pour réviser",
        "Génère un quiz sur ce sujet"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-blue-50/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 via-purple-500 to-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                className="text-white hover:bg-white/20 transition-colors"
                onClick={() => router.push('/classroom/courses')}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <Button
                variant="ghost"
                className="text-white hover:bg-white/20 transition-colors px-4"
                onClick={() => router.push('/dashboard')}
              >
                <Home className="h-4 w-4 mr-2" />
                Tableau de bord
              </Button>
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-3">
                  <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                    <Bot className="h-6 w-6" />
                  </div>
                  Assistant IA d'Apprentissage
                </h1>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="secondary" className="bg-white/20 text-white border-0">
                    <Zap className="h-3 w-3 mr-1" />
                    Propulsé par Groq
                  </Badge>
                  <Badge variant="secondary" className="bg-white/20 text-white border-0">
                    llama-3.3-70b-versatile
                  </Badge>
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                onClick={clearConversation}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Effacer
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            {/* Course Context */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Contexte du cours</CardTitle>
              </CardHeader>
              <CardContent>
                <select
                  className="w-full p-2 border rounded-lg text-sm"
                  value={selectedCourse}
                  onChange={(e) => setSelectedCourse(e.target.value)}
                >
                  <option value="">Aucun cours sélectionné</option>
                  {courses.map((course) => (
                    <option key={course.id} value={course.id}>
                      {course.nom}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-muted-foreground mt-2">
                  Sélectionnez un cours pour obtenir des réponses contextuelles
                </p>
              </CardContent>
            </Card>

            {/* Quick Prompts */}
            <Card className="border-purple-100">
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-purple-600" />
                  Suggestions rapides
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {quickPrompts.map((category, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
                      <category.icon className="h-3 w-3" />
                      {category.title}
                    </div>
                    {category.prompts.map((prompt, pidx) => (
                      <Button
                        key={pidx}
                        variant="outline"
                        size="sm"
                        className="w-full justify-start text-left h-auto py-2 px-3 hover:bg-purple-50 hover:border-purple-200 transition-colors"
                        onClick={() => setInput(prompt)}
                      >
                        <span className="text-xs line-clamp-2">{prompt}</span>
                      </Button>
                    ))}
                    {idx < quickPrompts.length - 1 && <Separator className="mt-3" />}
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Features */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Capacités</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-xs space-y-2 text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <Sparkles className="h-3 w-3 mt-0.5 flex-shrink-0 text-purple-500" />
                    <span>Explications de concepts</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Sparkles className="h-3 w-3 mt-0.5 flex-shrink-0 text-purple-500" />
                    <span>Aide aux devoirs</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Sparkles className="h-3 w-3 mt-0.5 flex-shrink-0 text-purple-500" />
                    <span>Conseils d'étude</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Sparkles className="h-3 w-3 mt-0.5 flex-shrink-0 text-purple-500" />
                    <span>Résumés de contenu</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Sparkles className="h-3 w-3 mt-0.5 flex-shrink-0 text-purple-500" />
                    <span>Génération d'exemples</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-[calc(100vh-200px)] flex flex-col shadow-lg border-purple-100">
              {/* Messages */}
              <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-white to-gray-50/30">
                {messages.map((message, index) => (
                  <div
                    key={message.id}
                    className={`flex gap-4 ${
                      message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                    } group`}
                  >
                    {/* Avatar */}
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md ${
                        message.role === 'user'
                          ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                          : message.isError
                          ? 'bg-gradient-to-br from-red-500 to-red-600 text-white'
                          : 'bg-gradient-to-br from-purple-500 to-purple-600 text-white'
                      }`}
                    >
                      {message.role === 'user' ? (
                        <User className="h-5 w-5" />
                      ) : (
                        <Bot className="h-5 w-5" />
                      )}
                    </div>

                    {/* Message Content */}
                    <div className="flex-1 space-y-2">
                      <div
                        className={`rounded-2xl p-4 shadow-sm ${
                          message.role === 'user'
                            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white ml-auto max-w-[85%]'
                            : message.isError
                            ? 'bg-red-50 text-red-900 border border-red-200 max-w-[85%]'
                            : 'bg-white border border-gray-200 max-w-[95%]'
                        }`}
                      >
                        {/* Render markdown-style content */}
                        <div className="prose prose-sm max-w-none">
                          {message.content.split('\n').map((line, i) => {
                            // Bold text **text**
                            if (line.includes('**')) {
                              const parts = line.split(/(\*\*.*?\*\*)/g);
                              return (
                                <p key={i} className={message.role === 'user' ? 'text-white' : ''}>
                                  {parts.map((part, j) => {
                                    if (part.startsWith('**') && part.endsWith('**')) {
                                      return <strong key={j}>{part.slice(2, -2)}</strong>;
                                    }
                                    return <span key={j}>{part}</span>;
                                  })}
                                </p>
                              );
                            }
                            // Bullet points
                            if (line.trim().startsWith('-')) {
                              return (
                                <li key={i} className="ml-4">
                                  {line.trim().substring(1).trim()}
                                </li>
                              );
                            }
                            // Regular text
                            return line.trim() ? (
                              <p key={i} className={message.role === 'user' ? 'text-white' : ''}>
                                {line}
                              </p>
                            ) : (
                              <br key={i} />
                            );
                          })}
                        </div>

                        {/* Timestamp */}
                        <div className="flex items-center justify-between mt-3 pt-2 border-t border-current/10">
                          <p
                            className={`text-xs ${
                              message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                            }`}
                          >
                            {message.timestamp.toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                      </div>

                      {/* Message Actions */}
                      {message.role === 'assistant' && !message.isError && (
                        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs"
                            onClick={() => copyToClipboard(message.content, message.id)}
                          >
                            {copiedId === message.id ? (
                              <>
                                <CheckCircle2 className="h-3 w-3 mr-1" />
                                Copié!
                              </>
                            ) : (
                              <>
                                <Copy className="h-3 w-3 mr-1" />
                                Copier
                              </>
                            )}
                          </Button>
                          {index > 0 && messages[index - 1]?.role === 'user' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 text-xs"
                              onClick={() => regenerateResponse(index - 1)}
                              disabled={loading}
                            >
                              <RefreshCw className="h-3 w-3 mr-1" />
                              Régénérer
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex gap-4">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                      <Bot className="h-5 w-5 animate-pulse" />
                    </div>
                    <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
                      <div className="flex gap-1.5">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </CardContent>

              {/* Input Area */}
              <div className="border-t bg-white p-4 space-y-3">
                {selectedCourse && (
                  <div className="flex items-center gap-2 px-3 py-2 bg-purple-50 border border-purple-200 rounded-lg">
                    <BookOpen className="h-4 w-4 text-purple-600" />
                    <span className="text-sm font-medium text-purple-900">
                      {courses.find(c => c.id === selectedCourse)?.nom}
                    </span>
                  </div>
                )}
                <div className="flex gap-3">
                  <Textarea
                    ref={inputRef}
                    className="flex-1 min-h-[80px] max-h-[200px] resize-y p-3 border-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    placeholder="Posez votre question ici... (Entrée pour envoyer, Shift+Entrée pour nouvelle ligne)"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={loading}
                  />
                  <Button
                    onClick={handleSend}
                    disabled={!input.trim() || loading}
                    className="self-end h-[80px] w-14 bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl transition-all"
                    size="lg"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
                  </Button>
                </div>
                <div className="flex items-center justify-between px-1">
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Sparkles className="h-3 w-3" />
                    L'IA peut faire des erreurs. Vérifiez les informations importantes.
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {input.length > 0 && `${input.length} caractères`}
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
