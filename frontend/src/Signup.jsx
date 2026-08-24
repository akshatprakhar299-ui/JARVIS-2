import { useState } from "react";

import {
  createUserWithEmailAndPassword
} from "firebase/auth";

import { auth } from "./firebase";

function Signup({ onSignup, onLogin }) {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSignup(event) {

    event.preventDefault();

    setError("");
    setLoading(true);

    try {

      const userCredential =
        await createUserWithEmailAndPassword(
          auth,
          email,
          password
        );

      onSignup(userCredential.user);

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

        <p>Create your account</p>

        <form onSubmit={handleSignup}>

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
            minLength="6"
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
            {loading ? "Creating..." : "Create Account"}
          </button>

        </form>

        <p>
          Already have an account?

          <button
            className="link-button"
            onClick={onLogin}
          >
            Login
          </button>

        </p>

      </div>

    </div>
  );
}

export default Signup;