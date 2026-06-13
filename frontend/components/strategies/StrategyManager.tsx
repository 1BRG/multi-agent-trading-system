"use client";

import React, { useState, useEffect, useRef } from "react";
import { generateAiStrategy } from "../../lib/strategy"; 
import { getChatMessages, createChatMessage, createChatThread } from "../../lib/chat";
import type { ChatMessage } from "../../types/chat";
import { ApiError } from "../../lib/api";

interface StrategyManagerProps {
  chatId?: string;
  onChatCreated?: (id: string) => void;
}

export default function StrategyManager({ chatId, onChatCreated }: StrategyManagerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [toast, setToast] = useState<{ title: string; message: string } | null>(null);

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

  const showErrorToast = (err: unknown) => {
    const fallback = {
      title: "Could not generate strategy",
      message: "That request failed right now. Please try again, simplify the prompt, or start a new chat.",
    };

    if (err instanceof ApiError) {
      const text = err.message.toLowerCase();

      if (text.includes("rebalance_frequency") || text.includes("not a valid choice")) {
        setToast({
          title: "Invalid schedule from AI",
          message: "The model returned an unsupported rebalance cadence. Please try again; we enforce daily/weekly/monthly/quarterly only.",
        });
        return;
      }

      if (text.includes("json") || text.includes("llm") || text.includes("empty response")) {
        setToast({
          title: "AI response unavailable",
          message: "Sorry, this request is beyond current model reliability. Try a shorter, more explicit prompt and run again.",
        });
        return;
      }

      if (err.status >= 500) {
        setToast({
          title: "Server issue",
          message: "Our AI service is temporarily unavailable. Please retry in a moment or start a fresh chat.",
        });
        return;
      }

      if (err.status === 400) {
        setToast({
          title: "Prompt needs adjustment",
          message: "Please make the request more specific (ticker, risk level, horizon, and rebalance frequency).",
        });
        return;
      }
    }

    setToast(fallback);
  };

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
    setToast(null);

    try {
      let currentThreadId: number | null = chatId ? Number(chatId) : null;

      if (!currentThreadId) {
        const generatedTitle = currentPrompt.length > 28 
          ? currentPrompt.substring(0, 28) + "..." 
          : currentPrompt;
        
        const newThread = await createChatThread(generatedTitle);
        currentThreadId = newThread.id;
        
        if (onChatCreated) onChatCreated(String(newThread.id));
      }

      if (currentThreadId === null) {
        throw new Error("Failed to create a chat thread.");
      }

      const threadId = currentThreadId;

      // 1. Save user message
      const userMsg = await createChatMessage(threadId, "user", currentPrompt);
      
      setMessages(prev => {
        if (prev.some(m => m.id === userMsg.id)) return prev;
        return [...prev, userMsg];
      });

      // 2. Ask AI
      const newStrategy = await generateAiStrategy(currentPrompt, threadId);

      // 3. Save AI message — include the strategy id and status so the UI can act on drafts
      const aiMsg = await createChatMessage(
        threadId,
        "assistant",
        newStrategy.description,
        { strategyConfig: newStrategy.config, strategyName: newStrategy.name, strategyId: newStrategy.id, strategyStatus: newStrategy.status }
      );
      
      setMessages(prev => {
        if (prev.some(m => m.id === aiMsg.id)) return prev;
        return [...prev, aiMsg];
      });

    } catch (err: any) {
      showErrorToast(err);
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
             
             {Boolean(msg.metadata?.strategyConfig) && (
               <>
                 <p className="eyebrow" style={{ marginBottom: "4px" }}>Deterministic Config:</p>
                 <pre style={{ background: "#172033", color: "#ffffff", padding: "12px", borderRadius: "6px", overflowX: "auto", fontSize: "13px", margin: 0 }}>
                   {JSON.stringify(msg.metadata?.strategyConfig, null, 2)}
                 </pre>
                {msg.metadata?.strategyId && msg.metadata?.strategyStatus === "draft" && (
                  <div style={{ marginTop: 8 }}>
                    <button
                      onClick={async () => {
                        const strategyId = msg.metadata?.strategyId;
                        if (!strategyId) return;

                        try {
                          setIsLoading(true);
                          const { approveStrategy } = await import("../../lib/strategy");
                          const updated = await approveStrategy(strategyId);
                          // update message metadata in-place
                          setMessages(prev => prev.map(m => m.id === msg.id ? { ...m, metadata: { ...m.metadata, strategyStatus: updated.status } } : m));
                        } catch (e: any) {
                          showErrorToast(e);
                        } finally {
                          setIsLoading(false);
                        }
                      }}
                      className="btn-approve"
                    >
                      Approve Strategy
                    </button>
                  </div>
                )}
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

      </div>

      {toast && (
        <div className="toast-stack" role="status" aria-live="polite">
          <div className="app-toast app-toast-error">
            <div className="close-bttn-toast">
              <button
                aria-label="Close notification"
                className="app-toast-close"
                onClick={() => setToast(null)}
                type="button"
              >
                x
              </button>
            </div>
            <div className="app-toast-title">{toast.title}</div>
            <p>{toast.message}</p>
          </div>
        </div>
      )}

      <form className="chat-composer" onSubmit={handleGenerate}>
        <input placeholder="Type your trading idea here..." type="text" value={prompt} onChange={(e) => setPrompt(e.target.value)} disabled={isLoading} />
        <button disabled={isLoading || !prompt.trim()} type="submit">Send</button>
      </form>
    </>
  );
}
