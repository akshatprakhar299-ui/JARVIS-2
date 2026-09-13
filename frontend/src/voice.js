export const SpeechRecognition =
  window.SpeechRecognition ||
  window.webkitSpeechRecognition;

export function speak(text, onEnd) {
  if (!window.speechSynthesis) {
    console.warn("Speech synthesis is not supported.");
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);

  utterance.rate = 0.95;
  utterance.pitch = 0.9;
  utterance.volume = 1;

  // Try to select a natural English voice
  const voices = window.speechSynthesis.getVoices();

  const preferredVoice =
    voices.find((voice) =>
      /Google UK English Male/i.test(voice.name)
    ) ||
    voices.find((voice) =>
      /Microsoft David/i.test(voice.name)
    ) ||
    voices.find((voice) =>
      /English/i.test(voice.lang)
    );

  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }

  if (onEnd) {
    utterance.onend = onEnd;
  }

  window.speechSynthesis.speak(utterance);
}