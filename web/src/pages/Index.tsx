import { useState } from 'react';
import RouteInput from '@/components/RouteInput';
import RouteDisplay from '@/components/RouteDisplay';
import { RouteResponse } from '@/types';

const Index = () => {

  const [responses, setResponses] = useState<RouteResponse[]>([]);
  const [hasInteracted, setHasInteracted] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-12">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-gray-900">Route Planner</h1>
          <p className="text-lg text-gray-600">
            Enter your route or use voice input to plan your journey
          </p>
        </div>

        <RouteInput setResponses={setResponses} setHasInteracted={setHasInteracted} />

        <div className="bg-white/30 backdrop-blur rounded-xl p-6 shadow-lg">
          <RouteDisplay responses={responses} hasInteracted={hasInteracted} />
        </div>
      </div>
    </div>
  );
};

export default Index;
