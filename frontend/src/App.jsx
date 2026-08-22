import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  // ============================================================
  // LOAD CHAT HISTORY
  // ============================================================

  useEffect(() => {
    loadHistory();
  }, []);

  // ============================================================
  // AUTO SCROLL
  // ============================================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  // ============================================================
  // LOAD HISTORY
  // ============================================================

  async function loadHistory() {
    try {
      const response = await fetch(`${API_URL}/history`);

      const data = await response.json();

      if (data.success) {
        setMessages(data.messages);
      }
    } catch (error) {
      console.error("Could not load history:", error);
    }
  }

  // ============================================================
  // SEND MESSAGE
  // ============================================================

  async function sendMessage() {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    // Immediately show user's message
    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: message,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          message: message,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Something went wrong");
      }

      // Add JARVIS response
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.message,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "I'm having trouble connecting to my backend. Please make sure JARVIS is running.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // ENTER KEY
  // ============================================================

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  // ============================================================
  // CLEAR CONVERSATION
  // ============================================================

  async function clearChat() {
    try {
      const response = await fetch(`${API_URL}/history`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (data.success) {
        setMessages([]);
      }
    } catch (error) {
      console.error("Could not clear history:", error);
    }
  }

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="jarvis-app">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="jarvis-header">

        <div className="brand">

          <div className="brand-orb">
            <span></span>
          </div>

          <div>
            <h1>JARVIS</h1>
            <p>PERSONAL AI ASSISTANT</p>
          </div>

        </div>

        <div className="header-right">

          <div className="status">
            <span className="status-dot"></span>
            ONLINE
          </div>

          <button
            className="clear-button"
            onClick={clearChat}
          >
            Clear
          </button>

        </div>

      </header>


      {/* ======================================================
          CHAT AREA
      ====================================================== */}

      <main className="chat-container">

        {messages.length === 0 ? (

          <div className="welcome">

            <div className="welcome-orb">
              <div className="orb-core"></div>
            </div>

            <h2>How can I assist you?</h2>

            <p>
              I'm JARVIS, your personal AI assistant.
            </p>

            <div className="suggestions">

              <button
                onClick={() =>
                  setInput("Explain artificial intelligence to me")
                }
              >
                Explain AI
              </button>

              <button
                onClick={() =>
                  setInput("Help me plan my day")
                }
              >
                Plan my day
              </button>

              <button
                onClick={() =>
                  setInput("Teach me something interesting")
                }
              >
                Teach me something
              </button>

            </div>

          </div>

        ) : (

          <div className="messages">

            {messages.map((message, index) => (

              <div
                key={index}
                className={`message-row ${message.role}`}
              >

                {message.role === "assistant" && (
                  <div className="message-avatar">
                    J
                  </div>
                )}

                <div
                  className={`message-bubble ${
                    message.error ? "error" : ""
                  }`}
                >
                  {message.content}
                </div>

              </div>

            ))}


            {/* =================================================
                TYPING INDICATOR
                ================================================= */}

            {loading && (

              <div className="message-row assistant">

                <div className="message-avatar">
                  J
                </div>

                <div className="message-bubble typing">

                  <span></span>
                  <span></span>
                  <span></span>

                </div>

              </div>

            )}

            <div ref={messagesEndRef}></div>

          </div>

        )}

      </main>


      {/* ======================================================
          INPUT
      ====================================================== */}

      <footer className="input-area">

        <div className="input-wrapper">

          <textarea
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask JARVIS anything..."
            rows="1"
            disabled={loading}
          />

          <button
            className="send-button"
            onClick={sendMessage}
            disabled={!input.trim() || loading}
          >
            ↑
          </button>

        </div>

        <p className="input-hint">
          Press Enter to send • Shift + Enter for a new line
        </p>

      </footer>

    </div>
  );
}

export default App;