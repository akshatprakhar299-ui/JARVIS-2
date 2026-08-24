import { useState } from "react";
import {
  signInWithEmailAndPassword
} from "firebase/auth";

import { auth } from "./firebase";

function Login({ onLogin, onSignup }) {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(event) {

    event.preventDefault();

    setError("");
    setLoading(true);

    try {

      const userCredential =
        await signInWithEmailAndPassword(
          auth,
          email,
          password
        );

      onLogin(userCredential.user);

    } catch (error) {

      setError(error.message);

    } finally {

      setLoading(false);

    }
  }

  return (
    <div className="auth-page">

      <div className="auth-card">

        <h1>JARVIS</h1>

        <p>Welcome back</p>

        <form onSubmit={handleLogin}>

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required
          />

          {error && (
            <p className="auth-error">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Login"}
          </button>

        </form>

        <p>
          Don't have an account?
          <button
            className="link-button"
            onClick={onSignup}
          >
            Sign up
          </button>
        </p>

      </div>

    </div>
  );
}

export default Login;