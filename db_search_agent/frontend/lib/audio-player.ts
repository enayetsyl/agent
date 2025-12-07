/**
 * Audio Player Utility
 * Handles audio output playback
 */

export async function startAudioPlayerWorklet(): Promise<[AudioWorkletNode, AudioContext]> {
  // 1. Create an AudioContext
  const audioContext = new AudioContext({
    sampleRate: 24000
  });

  // 2. Load your custom processor code
  const workletURL = new URL('/js/pcm-player-processor.js', window.location.origin);
  await audioContext.audioWorklet.addModule(workletURL);

  // 3. Create an AudioWorkletNode
  const audioPlayerNode = new AudioWorkletNode(audioContext, 'pcm-player-processor');

  // 4. Connect to the destination
  audioPlayerNode.connect(audioContext.destination);

  // The audioPlayerNode.port is how we send messages (audio data) to the processor
  return [audioPlayerNode, audioContext];
}

/**
 * Convert base64 string to ArrayBuffer
 */
export function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Convert ArrayBuffer to base64 string
 */
export function arrayBufferToBase64(buffer: ArrayBuffer): string {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

