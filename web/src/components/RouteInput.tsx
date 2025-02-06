import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { RouteResponse } from '@/types';

interface RouteInputProps {
  setResponses: React.Dispatch<React.SetStateAction<RouteResponse[]>>;
  setHasInteracted: React.Dispatch<React.SetStateAction<boolean>>;
}

const RouteInput: React.FC<RouteInputProps> = ({ setResponses, setHasInteracted }) => {
  // États
  const [isRecording, setIsRecording] = useState(false);
  const [routeText, setRouteText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioData, setAudioData] = useState<number[]>([]);
  const [recordedAudio, setRecordedAudio] = useState<Blob | null>(null);

  // Références pour les ressources (MediaRecorder, AudioContext, etc.)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const isRecordingRef = useRef(isRecording);

  // Mettre à jour la référence mutable de isRecording pour la visualisation
  useEffect(() => {
    isRecordingRef.current = isRecording;
  }, [isRecording]);

  // Nettoyage lors du démontage du composant
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // Démarrage de l'enregistrement avec configuration du contexte audio et de la visualisation
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setRecordedAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      visualize();
    } catch (error) {
      toast.error("Impossible d'accéder au microphone");
      console.error(error);
    }
  };

  // Fonction de visualisation qui utilise requestAnimationFrame
  const visualize = () => {
    if (!analyserRef.current) return;
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

    const draw = () => {
      if (!isRecordingRef.current) return; // Utilisation de la référence pour éviter une fermeture figée
      analyserRef.current!.getByteFrequencyData(dataArray);
      const visualData = Array.from(dataArray.slice(0, 20)).map(value => value / 255);
      setAudioData(visualData);
      animationFrameRef.current = requestAnimationFrame(draw);
    };

    draw();
  };

  // Arrêt de l'enregistrement et nettoyage des ressources
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      setAudioData([]);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    }
  };

  // Envoi du texte de la route à l'API
  const handleSubmit = async () => {
    if (!routeText.trim()) return;
    const API_URL = import.meta.env.VITE_API_URL;

    try {
      setIsProcessing(true);
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json'
        },
        body: JSON.stringify({ text: routeText }),
      });
      if (!response.ok) {
        throw new Error('Erreur lors de la requête');
      }
      const responses = await response.json();
      setResponses(responses);
      setHasInteracted(true);
    } catch (error) {
      console.error('Erreur:', error);
      toast.error("Erreur lors de l'envoi de la route");
    } finally {
      setIsProcessing(false);
    }
  };

  // Téléchargement de l'audio enregistré
  const handleDownloadAudio = useCallback(() => {
    if (!recordedAudio) return;
    const url = URL.createObjectURL(recordedAudio);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'recording.webm';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [recordedAudio]);

  // Envoi de l'audio à une API via un formulaire multipart/form-data
  const handleUploadAudio = async () => {
    if (!recordedAudio) return;
    const formData = new FormData();
    formData.append('audio', recordedAudio, 'recording.webm');
    const API_VOICE_URL = import.meta.env.VITE_API_VOICE_URL || import.meta.env.VITE_API_URL;
    try {
      const response = await fetch(API_VOICE_URL, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Erreur lors de l'envoi de l'audio");
      }
      const data = await response.json();
      console.log("Réponse de l'API audio:", data);
      toast.success("Audio envoyé avec succès !");
    } catch (error) {
      console.error("Échec de l'envoi:", error);
      toast.error("Échec de l'envoi de l'audio");
    }
  };

  return (
      <div className="space-y-4 w-full max-w-2xl mx-auto">
        {/* Zone de saisie du texte */}
        <div className="relative">
          <Textarea
              value={routeText}
              onChange={(e) => setRouteText(e.target.value)}
              placeholder="Entrez votre route (ex : 'New York à Los Angeles via Chicago')"
              className="min-h-[120px] pr-12 text-lg"
          />
          {/* Bouton pour démarrer/arrêter l'enregistrement */}
          <div className="absolute right-2 bottom-2">
            <Button
                size="icon"
                variant={isRecording ? "destructive" : "secondary"}
                onClick={isRecording ? stopRecording : startRecording}
                className="rounded-full"
                disabled={isProcessing}
            >
              {isProcessing ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
              ) : isRecording ? (
                  <MicOff className="h-5 w-5" />
              ) : (
                  <Mic className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>

        {/* Visualisation de l'audio pendant l'enregistrement */}
        {isRecording && (
            <div className="h-16 bg-gray-50 rounded-lg p-2 flex items-center justify-center gap-1 overflow-hidden">
              {audioData.map((value, index) => (
                  <div
                      key={index}
                      className="w-2 bg-primary rounded-full transition-all duration-75"
                      style={{
                        height: `${Math.max(value * 100, 15)}%`,
                        transform: `scaleY(${Math.max(value, 0.15)})`
                      }}
                  />
              ))}
            </div>
        )}

        {/* Bouton d'envoi du texte */}
        <Button
            onClick={handleSubmit}
            className="w-full"
            disabled={!routeText.trim() || isProcessing}
        >
          Show Route
        </Button>

        {/* Si un enregistrement audio existe, on affiche un lecteur et des boutons pour télécharger et envoyer */}
        {recordedAudio && (
            <div className="space-y-4">
              <audio
                  controls
                  src={URL.createObjectURL(recordedAudio)}
                  className="w-full"
              />
              <div className="flex gap-2">
                <Button onClick={handleDownloadAudio} variant="outline">
                  Télécharger l'audio
                </Button>
                <Button onClick={handleUploadAudio} variant="secondary">
                  Envoyer l'audio
                </Button>
              </div>
            </div>
        )}
      </div>
  );
};

export default RouteInput;
