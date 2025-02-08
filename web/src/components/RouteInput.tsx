import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, Loader2, Upload, X } from 'lucide-react';
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
  const stopRecording = async () => {
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

    if (recordedAudio) {
        const API_URL = import.meta.env.VITE_API_URL_VOICE;
        const formData = new FormData();
        formData.append('file', recordedAudio, 'audio.webm');

        try {
          const response = await fetch(API_URL, {
            method: 'POST',
            body: formData,
          });
          if (response.ok) {
            const data = await response.json();
            setRouteText(data.transcribedText);
          } else {
            toast.error('Erreur lors de la transcription');
          }
        }
        catch (error) {
          console.error(error);
          toast.error("Une erreur est survenue lors de l'envoi au backend.");
        }
    }
    else {
      toast.error("Aucun fichier audio enregistré");
    }
  };

  // Envoi du texte de la route à l'API
  const handleSubmit = async () => {
    if (!routeText.trim()) return;

    let headers = new Headers();

    const body = JSON.stringify({ text: routeText });
    const API_URL = import.meta.env.VITE_API_URL_MODEL;

    try {
      setIsProcessing(true);

      headers.append('Content-Type', 'application/json');
      headers.append('Accept', 'application/json');

      const { text } = JSON.parse(body);
      const lines = text.split("\n");
      const filteredLines = lines.filter(line => line.trim() !== '');
      const responses: RouteResponse[] = [];

      for (let i = 0; i < filteredLines.length; i++) {
        let ID = 0;
        let text = filteredLines[i];

        if (text.includes(",") && /^\d/.test(text)) {
          [ID, text] = text.split(",", 2);
        }

        const response = await fetch(API_URL, {
          method: 'POST',
          headers,
          body: JSON.stringify({text}),
        });

        if (!response.ok) {
          throw new Error('Failed to fetch');
        }

        const one_responses = await response.json();
        const responseWithID: RouteResponse = {
          IDsentence: ID,
          responsesmodel: one_responses.responsesmodel,
          text: one_responses.text,
          itinerary: one_responses.itinerary,
          error_nlp: one_responses.error_nlp,
          error_route: one_responses.error_route,
        };

        responses.push(responseWithID);
      }

      console.log(responses);
      setResponses(responses);
      setHasInteracted(true);
    } catch (error) {
      console.error(error);
      toast.error("Erreur lors de l'envoi de la route");
    } finally {
      setIsProcessing(false);
    }
  };


  return (
    <div className="space-y-4 w-full max-w-2xl mx-auto flex-col">
      <Textarea
        value={routeText}
        onChange={(e) => setRouteText(e.target.value)}
        placeholder="Enter your route (e.g., 'New York to Los Angeles via Chicago')"
        className="min-h-[120px] pr-12 text-lg"
      />

      <div className='flex flex-row gap-4 justify-end'>
        <Button
          size="icon"
          variant={isRecording ? "destructive" : "secondary"}
          onClick={() => {
            setRouteText('');
            isRecording ? stopRecording() : startRecording();
          }}
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

        <Button
          size="icon"
          variant="secondary"
          onClick={() => {
            setRouteText('');
            document.getElementById('fileInput')?.click()
          }}
          className="rounded-full"
          disabled={isProcessing}
          title="Télécharger un fichier txt ou m4a"
        >
          <Upload className="w-5 h-5" />
          <input
            type="file"
            id="fileInput"
            accept=".txt, .m4a"
            style={{ display: 'none' }}
            onChange={async (e) => {
              const file = e.target.files?.[0];
              if (file) {

                if (!file.name.endsWith(".txt") && !file.name.endsWith(".m4a")) {
                  alert("Erreur : Seuls les fichiers .txt ou .m4a sont autorisés !");
                  return;
                }

                if (file.name.endsWith(".txt")) {
                  const reader = new FileReader();
                  reader.onload = (event) => {
                    if (event.target?.result) {
                      setRouteText(event.target.result as string);
                    }
                  };
                  reader.readAsText(file);
                  return;
                }

                if (file.name.endsWith(".m4a")) {
                  const API_URL = import.meta.env.VITE_API_URL_VOICE;
                  const formData = new FormData();
                  formData.append('file', file, file.name);

                  try {
                    const response = await fetch(API_URL, {
                      method: 'POST',
                      body: formData,
                    });
                    if (response.ok) {
                      const data = await response.json();
                      setRouteText(data.transcribedText);
                    } else {
                      toast.error('Erreur lors de la transcription');
                    }
                  }
                  catch (error) {
                    console.error(error);
                    toast.error("Une erreur est survenue lors de l'envoi du fichier.");
                  }
                }
              }
            }
            }
          />
        </Button>

        <Button
          size="icon"
          variant="secondary"
          onClick={() => setRouteText('')}
          className="rounded-full"
          disabled={isProcessing || !routeText}
          title="Effacer le texte du trajet"
        >
          <X className="w-5 h-5" />
        </Button>
      </div>

      <Button
        onClick={handleSubmit}
        className="w-full"
        disabled={!routeText.trim() || isProcessing}
      >
        Show Route
      </Button>

    </div >
  );
};

export default RouteInput;
