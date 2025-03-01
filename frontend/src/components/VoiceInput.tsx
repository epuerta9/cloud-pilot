import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Microphone, SpeakerHigh, SpeakerX } from 'phosphor-react';
import './VoiceInput.css';

interface VoiceInputProps {
  isRecording: boolean;
  toggleRecording: () => void;
  onTranscript: (text: string) => void;
  disabled?: boolean;
  lang?: string;
}

type SpeechRecognitionErrorCode = 
  | 'no-speech'
  | 'audio-capture'
  | 'not-allowed'
  | 'network'
  | 'aborted'
  | 'service-not-allowed'
  | 'bad-grammar';

interface SpeechRecognitionErrorEvent extends Event {
  error: SpeechRecognitionErrorCode;
  message?: string;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ 
  isRecording, 
  toggleRecording, 
  onTranscript,
  disabled = false,
  lang = 'en-US'
}) => {
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [volume, setVolume] = useState<number>(0);
  const [isSupported, setIsSupported] = useState<boolean>(true);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  
  const recognitionRef = useRef<any>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const lastTranscriptRef = useRef<string>('');
  
  // Initialize audio context and analyser
  const initAudioContext = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
    }
  }, []);

  // Check for browser support and permissions
  useEffect(() => {
    const checkSupport = async () => {
      const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (!SpeechRecognition) {
        setIsSupported(false);
        setErrorMessage('Speech recognition not supported in this browser');
        return;
      }

      try {
        const permissionStatus = await navigator.permissions.query({ name: 'microphone' as PermissionName });
        setHasPermission(permissionStatus.state === 'granted');
        
        permissionStatus.onchange = () => {
          setHasPermission(permissionStatus.state === 'granted');
        };
      } catch (error) {
        console.warn('Could not query microphone permission:', error);
      }
    };

    checkSupport();
  }, []);

  // Initialize SpeechRecognition
  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = true;
    recognitionRef.current.interimResults = true;
    recognitionRef.current.lang = lang;

    recognitionRef.current.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join('');
      
      const isFinal = event.results[0].isFinal;
      
      if (isFinal) {
        const newText = transcript.slice(lastTranscriptRef.current.length);
        if (newText.trim()) {
          onTranscript(newText);
        }
        lastTranscriptRef.current = transcript;
      }
    };

    recognitionRef.current.onerror = (event: SpeechRecognitionErrorEvent) => {
      const errorMessages: Record<SpeechRecognitionErrorCode, string> = {
        'no-speech': 'No speech detected. Please try again.',
        'audio-capture': 'No microphone was found.',
        'not-allowed': 'Microphone access denied.',
        'network': 'Network error occurred.',
        'aborted': 'Recording was cancelled.',
        'service-not-allowed': 'Speech recognition not allowed.',
        'bad-grammar': 'Speech grammar error.'
      };

      setErrorMessage(errorMessages[event.error] || `Error: ${event.error}`);
      if (isRecording) {
        toggleRecording();
      }
    };

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isSupported, lang, isRecording, toggleRecording, onTranscript]);

  // Handle volume visualization
  const analyzeVolume = useCallback(() => {
    if (!analyserRef.current || !mediaStreamRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    // Calculate average volume
    const average = dataArray.reduce((acc, val) => acc + val, 0) / dataArray.length;
    setVolume(average / 128); // Normalize to 0-1

    animationFrameRef.current = requestAnimationFrame(analyzeVolume);
  }, []);

  // Start recording
  const startRecording = useCallback(async () => {
    try {
      setErrorMessage('');
      lastTranscriptRef.current = '';
      
      if (!isSupported) {
        throw new Error('Speech recognition not supported');
      }

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      setHasPermission(true);

      // Initialize audio context and start analyzing
      initAudioContext();
      if (audioContextRef.current && analyserRef.current) {
        const source = audioContextRef.current.createMediaStreamSource(stream);
        source.connect(analyserRef.current);
        analyzeVolume();
      }

      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Error accessing microphone');
      setHasPermission(false);
      toggleRecording();
    }
  }, [toggleRecording, isSupported, initAudioContext, analyzeVolume]);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        console.warn('Error stopping recognition:', e);
      }
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    setVolume(0);
  }, []);

  // Handle recording state changes
  useEffect(() => {
    if (isRecording) {
      startRecording();
    } else {
      stopRecording();
    }

    return () => {
      stopRecording();
    };
  }, [isRecording, startRecording, stopRecording]);

  // Get appropriate icon based on state
  const getIcon = () => {
    if (!isSupported) return <SpeakerX size={20} />;
    if (isRecording) return <SpeakerHigh size={20} weight="fill" style={{ transform: `scale(${1 + volume * 0.2})` }} />;
    return <Microphone size={20} weight={isRecording ? "fill" : "regular"} />;
  };

  return (
    <div className="voice-input-container">
      {errorMessage && (
        <div className="voice-error-message" role="alert">
          {errorMessage}
        </div>
      )}
      <button
        className={`voice-button ${isRecording ? 'recording' : ''} ${disabled ? 'disabled' : ''} ${!isSupported ? 'unsupported' : ''}`}
        onClick={disabled || !isSupported ? undefined : toggleRecording}
        aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
        disabled={disabled || !isSupported}
        title={!isSupported 
          ? 'Speech recognition not supported in this browser' 
          : hasPermission === false 
            ? 'Microphone access denied'
            : isRecording 
              ? 'Stop recording' 
              : 'Start voice input'
        }
      >
        {getIcon()}
      </button>
    </div>
  );
};

export default VoiceInput;
