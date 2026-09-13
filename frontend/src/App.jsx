import {
  useEffect,
  useRef,
  useState,
  useCallback,
} from "react";

import {
  onAuthStateChanged,
  signOut,
} from "firebase/auth";

import { auth } from "./firebase";

import Login from "./Login";
import Signup from "./Signup";

import "./App.css";


// ============================================================
// CONFIGURATION
// ============================================================

const API_URL = "http://127.0.0.1:8000";


// ============================================================
// BROWSER SPEECH RECOGNITION
// ============================================================

const SpeechRecognitionAPI =
  window.SpeechRecognition ||
  window.webkitSpeechRecognition;


// ============================================================
// APP
// ============================================================

function App() {

  // ============================================================
  // AUTHENTICATION
  // ============================================================

  const [user, setUser] = useState(undefined);

  const [showSignup, setShowSignup] = useState(false);


  // ============================================================
  // CHAT
  // ============================================================

  const [messages, setMessages] = useState([]);

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);


  // ============================================================
  // VOICE
  // ============================================================

  const [voiceEnabled, setVoiceEnabled] = useState(false);

  const [listening, setListening] = useState(false);


  // ============================================================
  // REFS
  // ============================================================

  const messagesEndRef = useRef(null);

  const recognitionRef = useRef(null);

  const shouldListenRef = useRef(false);

  const speakingRef = useRef(false);

  const voiceModeRef = useRef("off");

  const voiceEnabledRef = useRef(false);

  const sendMessageRef = useRef(null);

  const restartTimerRef = useRef(null);


  // ============================================================
  // FIREBASE AUTH
  // ============================================================

  useEffect(() => {

    const unsubscribe =
      onAuthStateChanged(
        auth,
        (currentUser) => {

          setUser(currentUser);

        }
      );


    return () => {

      unsubscribe();

    };

  }, []);


  // ============================================================
  // LOAD HISTORY
  // ============================================================

  useEffect(() => {

    if (user) {

      loadHistory();

    }

  }, [user]);


  // ============================================================
  // AUTO SCROLL
  // ============================================================

  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages, loading]);


  // ============================================================
  // AUTH TOKEN
  // ============================================================

  async function getAuthToken() {

    if (!auth.currentUser) {

      throw new Error(
        "User is not authenticated."
      );

    }


    return await auth.currentUser.getIdToken();

  }


  // ============================================================
  // LOAD CHAT HISTORY
  // ============================================================

  async function loadHistory() {

    try {

      const token =
        await getAuthToken();


      const response =
        await fetch(
          `${API_URL}/history`,
          {
            method: "GET",

            headers: {
              "Authorization":
                `Bearer ${token}`,
            },
          }
        );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Could not load history."
        );

      }


      if (data.success) {

        setMessages(
          data.messages || []
        );

      }

    } catch (error) {

      console.error(
        "Could not load history:",
        error
      );

    }

  }


  // ============================================================
  // TEXT TO SPEECH
  // ============================================================

  function speakText(
    text,
    onFinished = null
  ) {

    if (!text) {

      if (onFinished) {

        onFinished();

      }

      return;

    }


    // ----------------------------------------------------------
    // Mark JARVIS as speaking BEFORE starting speech.
    // This prevents the microphone from processing JARVIS.
    // ----------------------------------------------------------

    speakingRef.current = true;


    if (!window.speechSynthesis) {

      console.warn(
        "Speech synthesis is not supported."
      );


      speakingRef.current = false;


      if (onFinished) {

        onFinished();

      }


      return;

    }


    // Stop previous speech.

    window.speechSynthesis.cancel();


    const utterance =
      new SpeechSynthesisUtterance(
        text
      );


    // ==========================================================
    // VOICE CHARACTER
    // ==========================================================

    utterance.rate = 0.92;

    utterance.pitch = 0.82;

    utterance.volume = 1;


    // ==========================================================
    // FIND A GOOD ENGLISH VOICE
    // ==========================================================

    const voices =
      window.speechSynthesis.getVoices();


    const preferredVoice =
      voices.find(
        (voice) =>
          /Microsoft David/i.test(
            voice.name
          )
      ) ||

      voices.find(
        (voice) =>
          /Microsoft Mark/i.test(
            voice.name
          )
      ) ||

      voices.find(
        (voice) =>
          /Google UK English Male/i.test(
            voice.name
          )
      ) ||

      voices.find(
        (voice) =>
          /English.*Male/i.test(
            voice.name
          )
      ) ||

      voices.find(
        (voice) =>
          /^en[-_]/i.test(
            voice.lang
          )
      );


    if (preferredVoice) {

      utterance.voice =
        preferredVoice;

    }


    // ==========================================================
    // SPEECH FINISHED
    // ==========================================================

    utterance.onend = () => {

      speakingRef.current = false;


      if (onFinished) {

        onFinished();

      }

    };


    // ==========================================================
    // SPEECH ERROR
    // ==========================================================

    utterance.onerror = () => {

      speakingRef.current = false;


      if (onFinished) {

        onFinished();

      }

    };


    window.speechSynthesis.speak(
      utterance
    );

  }


  // ============================================================
  // START RECOGNITION SAFELY
  // ============================================================

  function startRecognition() {

    const recognition =
      recognitionRef.current;


    if (!recognition) {

      return;

    }


    if (
      !shouldListenRef.current
    ) {

      return;

    }


    if (
      speakingRef.current
    ) {

      return;

    }


    if (
      voiceModeRef.current !== "wake" &&
      voiceModeRef.current !== "question"
    ) {

      return;

    }


    try {

      recognition.start();

    } catch (error) {

      // Chrome throws InvalidStateError if
      // recognition is already running.
      // That's harmless.

      console.log(
        "Recognition start:",
        error.message
      );

    }

  }


  // ============================================================
  // STOP RECOGNITION
  // ============================================================

  function stopRecognition() {

    const recognition =
      recognitionRef.current;


    if (!recognition) {

      return;

    }


    try {

      recognition.stop();

    } catch {}

  }


  // ============================================================
  // SEND MESSAGE
  // ============================================================

  const sendMessage = useCallback(
    async (voiceMessage = null) => {

      const message =
        voiceMessage !== null
          ? voiceMessage.trim()
          : input.trim();


      if (!message) {

        return;

      }


      if (!user) {

        return;

      }


      if (loading) {

        return;

      }


      // ========================================================
      // IF THIS IS A VOICE QUESTION
      // ========================================================

      const isVoiceQuestion =
        voiceMessage !== null;


      if (isVoiceQuestion) {

        voiceModeRef.current =
          "processing";

        stopRecognition();

      }


      // ========================================================
      // DISPLAY USER MESSAGE
      // ========================================================

      setMessages(
        (previous) => [

          ...previous,

          {
            role: "user",
            content: message,
          },

        ]
      );


      setInput("");

      setLoading(true);


      try {

        // ======================================================
        // FIREBASE TOKEN
        // ======================================================

        const token =
          await getAuthToken();


        // ======================================================
        // BACKEND REQUEST
        // ======================================================

        const response =
          await fetch(
            `${API_URL}/chat`,
            {
              method: "POST",

              headers: {

                "Content-Type":
                  "application/json",

                "Authorization":
                  `Bearer ${token}`,

              },

              body: JSON.stringify({

                message: message,

              }),

            }
          );


        // ======================================================
        // HANDLE NON-JSON RESPONSE
        // ======================================================

        let data;

        try {

          data =
            await response.json();

        } catch {

          throw new Error(
            `Backend returned HTTP ${response.status}`
          );

        }


        // ======================================================
        // AUTH ERROR
        // ======================================================

        if (
          response.status === 401
        ) {

          throw new Error(
            "Your login session has expired. Please login again."
          );

        }


        // ======================================================
        // BACKEND ERROR
        // ======================================================

        if (
          !response.ok ||
          !data.success
        ) {

          throw new Error(
            data.error ||
            data.detail ||
            "Something went wrong with JARVIS."
          );

        }


        // ======================================================
        // ASSISTANT RESPONSE
        // ======================================================

        const assistantMessage =
          data.message ||
          "I couldn't generate a response.";


        setMessages(
          (previous) => [

            ...previous,

            {
              role: "assistant",
              content: assistantMessage,
            },

          ]
        );


        // ======================================================
        // VOICE RESPONSE
        // ======================================================

        if (
          isVoiceQuestion &&
          voiceEnabledRef.current &&
          shouldListenRef.current
        ) {

          voiceModeRef.current =
            "speaking";


          speakText(
            assistantMessage,
            () => {

              // ------------------------------------------------
              // JARVIS HAS FINISHED SPEAKING.
              //
              // NOW AND ONLY NOW do we return to wake mode.
              // ------------------------------------------------

              if (
                shouldListenRef.current &&
                voiceEnabledRef.current
              ) {

                voiceModeRef.current =
                  "wake";


                setTimeout(() => {

                  startRecognition();

                }, 500);

              } else {

                voiceModeRef.current =
                  "off";

              }

            }
          );

        } else {

          // ----------------------------------------------------
          // If it was typed input, don't activate voice.
          // If voice mode somehow disappeared, return to wake.
          // ----------------------------------------------------

          if (
            isVoiceQuestion &&
            shouldListenRef.current
          ) {

            voiceModeRef.current =
              "wake";

            setTimeout(() => {

              startRecognition();

            }, 500);

          }

        }

      } catch (error) {

        console.error(
          "Chat error:",
          error
        );


        const errorMessage =
          error.message ||
          "I'm having trouble connecting to my backend.";


        setMessages(
          (previous) => [

            ...previous,

            {
              role: "assistant",
              content: errorMessage,
              error: true,
            },

          ]
        );


        // ======================================================
        // SPEAK ERROR IF VOICE QUESTION
        // ======================================================

        if (
          isVoiceQuestion &&
          voiceEnabledRef.current &&
          shouldListenRef.current
        ) {

          voiceModeRef.current =
            "speaking";


          speakText(
            errorMessage,
            () => {

              if (
                shouldListenRef.current &&
                voiceEnabledRef.current
              ) {

                voiceModeRef.current =
                  "wake";


                setTimeout(() => {

                  startRecognition();

                }, 500);

              }

            }
          );

        }

      } finally {

        setLoading(false);

      }

    },

    [
      input,
      user,
      loading,
    ]
  );


  // ============================================================
  // KEEP LATEST SEND FUNCTION FOR SPEECH CALLBACK
  // ============================================================

  useEffect(() => {

    sendMessageRef.current =
      sendMessage;

  }, [sendMessage]);


  // ============================================================
  // VOICE RECOGNITION INITIALIZATION
  // ============================================================

  useEffect(() => {

    if (!user) {

      return;

    }


    if (!SpeechRecognitionAPI) {

      console.warn(
        "Speech recognition is not supported in this browser."
      );

      return;

    }


    const recognition =
      new SpeechRecognitionAPI();


    recognition.continuous =
      true;


    recognition.interimResults =
      true;


    recognition.lang =
      "en-IN";


    recognition.maxAlternatives =
      1;


    recognitionRef.current =
      recognition;


    // ==========================================================
    // ON START
    // ==========================================================

    recognition.onstart = () => {

      setListening(true);

    };


    // ==========================================================
    // ON END
    // ==========================================================

    recognition.onend = () => {

      setListening(false);


      // NEVER restart while JARVIS is speaking.

      if (
        speakingRef.current
      ) {

        return;

      }


      // NEVER restart when voice mode is off.

      if (
        !shouldListenRef.current ||
        !voiceEnabledRef.current
      ) {

        return;

      }


      // Only wake/question modes should restart.

      if (
        voiceModeRef.current !== "wake" &&
        voiceModeRef.current !== "question"
      ) {

        return;

      }


      // Clear previous timer.

      if (
        restartTimerRef.current
      ) {

        clearTimeout(
          restartTimerRef.current
        );

      }


      restartTimerRef.current =
        setTimeout(() => {

          startRecognition();

        }, 400);

    };


    // ==========================================================
    // ON ERROR
    // ==========================================================

    recognition.onerror = (event) => {

      console.log(
        "Speech recognition:",
        event.error
      );


      if (
        event.error === "not-allowed" ||
        event.error === "service-not-allowed"
      ) {

        shouldListenRef.current =
          false;


        voiceEnabledRef.current =
          false;


        setVoiceEnabled(false);

        setListening(false);


        voiceModeRef.current =
          "off";

      }

    };


    // ==========================================================
    // ON RESULT
    // ==========================================================

    recognition.onresult = (event) => {

      // ========================================================
      // CRITICAL:
      // Ignore EVERYTHING while JARVIS is speaking.
      // This prevents JARVIS hearing himself.
      // ========================================================

      if (
        speakingRef.current
      ) {

        return;

      }


      if (
        !shouldListenRef.current
      ) {

        return;

      }


      // ========================================================
      // WAKE WORD MODE
      // ========================================================

      if (
        voiceModeRef.current === "wake"
      ) {

        let transcript = "";


        for (
          let i = event.resultIndex;
          i < event.results.length;
          i++
        ) {

          transcript +=
            event.results[i][0].transcript;

        }


        transcript =
          transcript.trim();


        if (!transcript) {

          return;

        }


        const lower =
          transcript.toLowerCase();


        // ------------------------------------------------------
        // Detect:
        //
        // "Hi JARVIS"
        // "Hey JARVIS"
        // "Hello JARVIS"
        // "JARVIS"
        // ------------------------------------------------------

        if (
          lower.includes("jarvis")
        ) {

          console.log(
            "Wake word detected:",
            transcript
          );


          // ----------------------------------------------------
          // IMPORTANT:
          // Change state FIRST.
          // ----------------------------------------------------

          voiceModeRef.current =
            "speaking";


          // ----------------------------------------------------
          // Stop microphone BEFORE speaking.
          // ----------------------------------------------------

          stopRecognition();


          // ----------------------------------------------------
          // Say ONLY "Yes boss."
          // ----------------------------------------------------

          speakText(
            "Yes boss.",
            () => {

              // ------------------------------------------------
              // "Yes boss." is COMPLETELY FINISHED.
              //
              // Now switch to question mode.
              // ------------------------------------------------

              if (
                shouldListenRef.current &&
                voiceEnabledRef.current
              ) {

                voiceModeRef.current =
                  "question";


                setTimeout(() => {

                  startRecognition();

                }, 600);

              }

            }
          );

        }


        return;

      }


      // ========================================================
      // QUESTION MODE
      // ========================================================

      if (
        voiceModeRef.current ===
        "question"
      ) {

        let transcript = "";


        for (
          let i = event.resultIndex;
          i < event.results.length;
          i++
        ) {

          transcript +=
            event.results[i][0].transcript;

        }


        transcript =
          transcript.trim();


        if (!transcript) {

          return;

        }


        const lastResult =
          event.results[
            event.results.length - 1
          ];


        // ------------------------------------------------------
        // We ONLY send FINAL speech.
        // ------------------------------------------------------

        if (
          lastResult &&
          lastResult.isFinal
        ) {

          const question =
            transcript.trim();


          if (!question) {

            return;

          }


          console.log(
            "Voice question:",
            question
          );


          // ----------------------------------------------------
          // Immediately change state so duplicate recognition
          // results cannot trigger another request.
          // ----------------------------------------------------

          voiceModeRef.current =
            "processing";


          stopRecognition();


          if (
            sendMessageRef.current
          ) {

            sendMessageRef.current(
              question
            );

          }

        }

      }

    };


    // ==========================================================
    // CLEANUP
    // ==========================================================

    return () => {

      shouldListenRef.current =
        false;


      voiceEnabledRef.current =
        false;


      if (
        restartTimerRef.current
      ) {

        clearTimeout(
          restartTimerRef.current
        );

      }


      try {

        recognition.stop();

      } catch {}


      if (
        window.speechSynthesis
      ) {

        window.speechSynthesis.cancel();

      }


      speakingRef.current =
        false;


      recognitionRef.current =
        null;

    };

  }, [user]);


  // ============================================================
  // START VOICE MODE
  // ============================================================

  function startVoiceMode() {

    if (!SpeechRecognitionAPI) {

      alert(
        "Speech recognition is not supported. Please use Google Chrome."
      );

      return;

    }


    if (!recognitionRef.current) {

      alert(
        "Voice system is still initializing. Please try again."
      );

      return;

    }


    // ==========================================================
    // ENABLE
    // ==========================================================

    shouldListenRef.current =
      true;


    voiceEnabledRef.current =
      true;


    voiceModeRef.current =
      "speaking";


    setVoiceEnabled(true);


    // ==========================================================
    // CONFIRM ACTIVATION
    //
    // Microphone stays OFF while saying this.
    // ==========================================================

    speakText(
      "Voice mode activated.",
      () => {

        if (
          shouldListenRef.current &&
          voiceEnabledRef.current
        ) {

          voiceModeRef.current =
            "wake";


          setTimeout(() => {

            startRecognition();

          }, 600);

        }

      }
    );

  }


  // ============================================================
  // STOP VOICE MODE
  // ============================================================

  function stopVoiceMode() {

    shouldListenRef.current =
      false;


    voiceEnabledRef.current =
      false;


    voiceModeRef.current =
      "off";


    setVoiceEnabled(false);

    setListening(false);


    if (
      restartTimerRef.current
    ) {

      clearTimeout(
        restartTimerRef.current
      );

    }


    stopRecognition();


    if (
      window.speechSynthesis
    ) {

      window.speechSynthesis.cancel();

    }


    speakingRef.current =
      false;

  }


  // ============================================================
  // TOGGLE VOICE
  // ============================================================

  function toggleVoiceMode() {

    if (voiceEnabled) {

      stopVoiceMode();

    } else {

      startVoiceMode();

    }

  }


  // ============================================================
  // KEYBOARD
  // ============================================================

  function handleKeyDown(event) {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      sendMessage();

    }

  }


  // ============================================================
  // CLEAR HISTORY
  // ============================================================

  async function clearChat() {

    try {

      const token =
        await getAuthToken();


      const response =
        await fetch(
          `${API_URL}/history`,
          {
            method: "DELETE",

            headers: {

              "Authorization":
                `Bearer ${token}`,

            },

          }
        );


      const data =
        await response.json();


      if (
        response.status === 401
      ) {

        throw new Error(
          "Authentication expired. Please login again."
        );

      }


      if (
        !response.ok ||
        !data.success
      ) {

        throw new Error(
          data.error ||
          data.detail ||
          "Could not clear history."
        );

      }


      setMessages([]);

    } catch (error) {

      console.error(
        "Could not clear history:",
        error
      );

    }

  }


  // ============================================================
  // LOGOUT
  // ============================================================

  async function handleLogout() {

    stopVoiceMode();


    try {

      await signOut(auth);


      setMessages([]);

      setInput("");


    } catch (error) {

      console.error(
        "Logout error:",
        error
      );

    }

  }


  // ============================================================
  // AUTH LOADING
  // ============================================================

  if (user === undefined) {

    return (

      <div className="auth-loading">

        <h1>
          JARVIS
        </h1>

        <p>
          Initializing authentication...
        </p>

      </div>

    );

  }


  // ============================================================
  // LOGIN
  // ============================================================

  if (
    !user &&
    !showSignup
  ) {

    return (

      <Login

        onLogin={(loggedInUser) => {

          setUser(loggedInUser);

        }}

        onSignup={() => {

          setShowSignup(true);

        }}

      />

    );

  }


  // ============================================================
  // SIGNUP
  // ============================================================

  if (
    !user &&
    showSignup
  ) {

    return (

      <Signup

        onSignup={(newUser) => {

          setUser(newUser);

        }}

        onLogin={() => {

          setShowSignup(false);

        }}

      />

    );

  }


  // ============================================================
  // MAIN JARVIS
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

            <h1>
              JARVIS
            </h1>

            <p>
              PERSONAL AI ASSISTANT
            </p>

          </div>

        </div>


        <div className="header-right">


          {/* ONLINE */}

          <div className="status">

            <span className="status-dot"></span>

            ONLINE

          </div>


          {/* VOICE */}

          <button
            className="voice-button"
            onClick={toggleVoiceMode}
            title={
              voiceEnabled
                ? "Disable voice mode"
                : "Enable voice mode"
            }
          >

            {listening
              ? "🎙 LISTENING"
              : voiceEnabled
                ? "🔊 VOICE ON"
                : "🎙 VOICE"
            }

          </button>


          {/* EMAIL */}

          <span className="user-email">

            {user.email}

          </span>


          {/* CLEAR */}

          <button
            className="clear-button"
            onClick={clearChat}
          >

            Clear

          </button>


          {/* LOGOUT */}

          <button
            className="logout-button"
            onClick={handleLogout}
          >

            Logout

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


            <h2>
              How can I assist you?
            </h2>


            <p>
              I'm JARVIS, your personal AI assistant.
            </p>


            <div className="suggestions">


              <button
                onClick={() =>
                  setInput(
                    "Explain artificial intelligence to me"
                  )
                }
              >

                Explain AI

              </button>


              <button
                onClick={() =>
                  setInput(
                    "Help me plan my day"
                  )
                }
              >

                Plan my day

              </button>


              <button
                onClick={() =>
                  setInput(
                    "Teach me something interesting"
                  )
                }
              >

                Teach me something

              </button>


            </div>


          </div>

        ) : (

          <div className="messages">


            {messages.map(
              (message, index) => (

                <div
                  key={index}
                  className={
                    `message-row ${message.role}`
                  }
                >


                  {message.role ===
                    "assistant" && (

                    <div className="message-avatar">

                      J

                    </div>

                  )}


                  <div
                    className={
                      `message-bubble ${
                        message.error
                          ? "error"
                          : ""
                      }`
                    }
                  >

                    {message.content}

                  </div>


                </div>

              )
            )}


            {/* =================================================
                LOADING
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


            <div
              ref={messagesEndRef}
            />


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
              setInput(
                event.target.value
              )
            }

            onKeyDown={handleKeyDown}

            placeholder={
              voiceEnabled
                ? "Say 'Hi JARVIS'..."
                : "Ask JARVIS anything..."
            }

            rows="1"

            disabled={loading}

          />


          <button

            className="send-button"

            onClick={() =>
              sendMessage()
            }

            disabled={
              !input.trim() ||
              loading
            }

          >

            ↑

          </button>


        </div>


        <p className="input-hint">

          {voiceEnabled

            ? listening
              ? "Listening for 'Hi JARVIS'..."
              : "Voice mode active"

            : "Press Enter to send • Shift + Enter for a new line"

          }

        </p>


      </footer>


    </div>

  );

}


export default App;