import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';

interface RouteResponse {
  responsesmodel: Array<JSON>;
  text: string;
}

interface RouteInputProps {
  setResponses: React.Dispatch<React.SetStateAction<RouteResponse[]>>;
}

const RouteInput: React.FC<RouteInputProps> = ({ setResponses }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [routeText, setRouteText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioData, setAudioData] = useState<number[]>([]);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number>();


  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
      };

      mediaRecorder.start();
      setIsRecording(true);
      visualize();
    } catch (error) {
      toast.error("Couldn't access microphone");
    }
  };

  const visualize = () => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    const draw = () => {
      if (!isRecording) return;
      analyserRef.current?.getByteFrequencyData(dataArray);
      
      // Take only a portion of the frequency data for visualization
      const visualData = Array.from(dataArray.slice(0, 20)).map(value => value / 255);
      setAudioData(visualData);
      
      animationFrameRef.current = requestAnimationFrame(draw);
    };
    
    draw();
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      setAudioData([]);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  };

  const handleSubmit = async () => {
    if (!routeText.trim()) return;
    let headers = new Headers();

    const body = JSON.stringify({ text: routeText });
  
    try {
      headers.append('Content-Type', 'application/json');
      headers.append('Accept', 'application/json');
      headers.append('Origin','http://127.0.0.1:5000');

      const response = await fetch('http://127.0.0.1:5000/api/route', {
        method: 'POST',
        headers,
        body, 
      });
  
      if (!response.ok) {
        throw new Error('Failed to fetch');
      }
  
      const responses = await response.json();
      console.log(responses); 
      setResponses(responses);

    } catch (error) {
      console.error('Error:', error, body);
    }
  };


  return (
    <div className="space-y-4 w-full max-w-2xl mx-auto">
      <div className="relative">
        <Textarea
          value={routeText}
          onChange={(e) => setRouteText(e.target.value)}
          placeholder="Enter your route (e.g., 'New York to Los Angeles via Chicago')"
          className="min-h-[120px] pr-12 text-lg"
        />
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
      
      <Button 
        onClick={handleSubmit} 
        className="w-full"
        disabled={!routeText.trim() || isProcessing}
      >
        Show Route
      </Button>
    </div>
  );
};

export default RouteInput;