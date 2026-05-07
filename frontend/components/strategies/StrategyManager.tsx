"use client";

import React, { useState, useEffect, useRef } from "react";
import { generateAiStrategy } from "../../lib/strategy"; 
import { getChatMessages, createChatMessage, createChatThread } from "../../lib/chat";
import type { ChatMessage } from "../../types/chat";

interface StrategyManagerProps {
  chatId?: string;
  onChatCreated?: (id: string) => void;
}

export default function StrategyManager({ chatId, onChatCreated }: StrategyManagerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const threadRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatId) {
      fetchMessages(Number(chatId));
    } else {
      setMessages([]);
    }
  }, [chatId]);

  useEffect(() => {
    if (threadRef.current) threadRef.current.scrollTop = threadRef.current.scrollHeight;
  }, [messages, isLoading]);

  const fetchMessages = async (currentChatId: number) => {
    try {
      const allMessages = await getChatMessages();
      const tabMessages = allMessages.filter(m => m.thread === currentChatId);
      setMessages(tabMessages); 
    } catch (err) {
      console.error("Failed to fetch messages", err);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    const currentPrompt = prompt;
    setPrompt(""); 
    setIsLoading(true);
    setError(null);

    try {
      let currentThreadId = chatId ? Number(chatId) : null;

      if (!currentThreadId) {
        const generatedTitle = currentPrompt.length > 28 
          ? currentPrompt.substring(0, 28) + "..." 
          : currentPrompt;
        
        const newThread = await createChatThread(generatedTitle);
        currentThreadId = newThread.id;
        
        if (onChatCreated) onChatCreated(String(newThread.id));
      }

      // 1. Save user message
      const userMsg = await createChatMessage(currentThreadId, "user", currentPrompt);
      
      setMessages(prev => {
        if (prev.some(m => m.id === userMsg.id)) return prev;
        return [...prev, userMsg];
      });

      // 2. Ask AI
      const newStrategy = await generateAiStrategy(currentPrompt);

      // 3. Save AI message
      const aiMsg = await createChatMessage(
        currentThreadId, 
        "assistant", 
        newStrategy.description, 
        { strategyConfig: newStrategy.config, strategyName: newStrategy.name }
      );
      
      setMessages(prev => {
        if (prev.some(m => m.id === aiMsg.id)) return prev;
        return [...prev, aiMsg];
      });

    } catch (err: any) {
      setError(err.message || "Failed to generate strategy.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="chat-thread" ref={threadRef}>
        {messages.length === 0 && !isLoading && (
          <article className="chat-message assistant">
            <strong>Strategy agent</strong>
            <p>Hello! Describe the trading strategy you want to build.</p>
          </article>
        )}

        {messages.map((msg) => (
           <article key={msg.id} className={`chat-message ${msg.role}`}>
             <strong>{msg.role === "user" ? "You" : "Strategy agent"}</strong>
             
             {msg.role === "assistant" && msg.metadata?.strategyName && (
               <h3 style={{ marginTop: "4px", marginBottom: "4px" }}>{msg.metadata.strategyName}</h3>
             )}
             
             <p style={{ marginTop: "4px", marginBottom: "12px" }}>{msg.content}</p>
             
             {msg.metadata?.strategyConfig && (
               <>
                 <p className="eyebrow" style={{ marginBottom: "4px" }}>Deterministic Config:</p>
                 <pre style={{ background: "#172033", color: "#ffffff", padding: "12px", borderRadius: "6px", overflowX: "auto", fontSize: "13px", margin: 0 }}>
                   {JSON.stringify(msg.metadata.strategyConfig, null, 2)}
                 </pre>
               </>
             )}
           </article>
        ))}

        {isLoading && (
          <article className="chat-message assistant">
            <strong>Strategy agent</strong>
            <p>Analyzing idea and generating deterministic ruleset...</p>
          </article>
        )}

        {error && (
          <article className="chat-message user" style={{ background: "#fff1f3", color: "#a11124" }}>
            <strong>System Error</strong><p>{error}</p>
          </article>
        )}
      </div>

      <form className="chat-composer" onSubmit={handleGenerate}>
        <input placeholder="Type your trading idea here..." type="text" value={prompt} onChange={(e) => setPrompt(e.target.value)} disabled={isLoading} />
        <button disabled={isLoading || !prompt.trim()} type="submit">Send</button>
      </form>
    </>
  );
}