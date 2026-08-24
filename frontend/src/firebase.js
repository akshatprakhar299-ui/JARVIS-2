import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyCgbTLBd-lEtCxloZxjyrzV72c7RiW-0qc",
  authDomain: "jarvis-ai-9c645.firebaseapp.com",
  projectId: "jarvis-ai-9c645",
  storageBucket: "jarvis-ai-9c645.firebasestorage.app",
  messagingSenderId: "183903575586",
  appId: "1:183903575586:web:e6ad668f92394b6ef5f47b",
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);