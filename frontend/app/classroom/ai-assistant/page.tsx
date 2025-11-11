'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { classroomApi } from '@/lib/classroom-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  ArrowLeft, 
  Send, 
  Bot, 
  User,
  Sparkles,
  BookOpen,
  Lightbulb,
  Target
} from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function AIAssistantPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Bonjour! Je suis votre assistant IA d'apprentissage. Je peux vous aider avec vos cours, répondre à vos questions, et vous fournir des explications. Comment puis-je vous aider aujourd'hui?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [courses, setCourses] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadCourses();
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

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await classroomApi.chatWithAI(
        input,
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
        content: "Désolé, je rencontre un problème. Veuillez réessayer dans un moment.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickPrompts = [
    {
      icon: BookOpen,
      text: "Explique-moi ce concept",
      prompt: "Peux-tu m'expliquer ce concept en termes simples?"
    },
    {
      icon: Lightbulb,
      text: "Donne-moi des exemples",
      prompt: "Peux-tu me donner quelques exemples pratiques?"
    },
    {
      icon: Target,
      text: "Comment étudier efficacement?",
      prompt: "Quelles sont les meilleures stratégies d'étude pour ce sujet?"
    },
    {
      icon: Sparkles,
      text: "Résume les points clés",
      prompt: "Peux-tu résumer les points clés à retenir?"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                className="text-white hover:bg-white/20"
                onClick={() => router.push('/classroom/courses')}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <Bot className="h-6 w-6" />
                  Assistant IA d'Apprentissage
                </h1>
                <p className="text-white/90 text-sm mt-1">
                  Propulsé par Groq (llama-3.3-70b-versatile) - Ultra rapide!
                </p>
              </div>
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
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Suggestions rapides</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {quickPrompts.map((prompt, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    className="w-full justify-start text-left h-auto py-2"
                    onClick={() => setInput(prompt.prompt)}
                  >
                    <prompt.icon className="h-4 w-4 mr-2 flex-shrink-0" />
                    <span className="text-xs">{prompt.text}</span>
                  </Button>
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
            <Card className="h-[calc(100vh-200px)] flex flex-col">
              {/* Messages */}
              <CardContent className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                    }`}
                  >
                    {/* Avatar */}
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-purple-500 text-white'
                      }`}
                    >
                      {message.role === 'user' ? (
                        <User className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4" />
                      )}
                    </div>

                    {/* Message Bubble */}
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      <p
                        className={`text-xs mt-2 ${
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
                ))}

                {loading && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-purple-500 text-white flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="bg-gray-100 rounded-lg p-4">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </CardContent>

              {/* Input Area */}
              <div className="border-t p-4">
                {selectedCourse && (
                  <div className="mb-2 text-xs text-muted-foreground flex items-center gap-1">
                    <BookOpen className="h-3 w-3" />
                    <span>
                      Contexte: {courses.find(c => c.id === selectedCourse)?.nom}
                    </span>
                  </div>
                )}
                <div className="flex gap-2">
                  <textarea
                    className="flex-1 p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
                    rows={2}
                    placeholder="Posez votre question ici... (Entrée pour envoyer, Shift+Entrée pour nouvelle ligne)"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={loading}
                  />
                  <Button
                    onClick={handleSend}
                    disabled={!input.trim() || loading}
                    className="self-end bg-purple-600 hover:bg-purple-700"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  L'IA peut faire des erreurs. Vérifiez les informations importantes.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
