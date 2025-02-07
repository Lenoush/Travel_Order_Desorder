import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { RouteResponse, RouteItem } from '@/types';

interface RouteDisplayProps {
  responses: RouteResponse[];
  hasInteracted: boolean;
}

const RouteDisplay: React.FC<RouteDisplayProps> = ({ responses, hasInteracted }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [showFormatted, setShowFormatted] = useState(false);

  
  const formattedResponses = responses.map((response) => {
    const isModelValid =
      Array.isArray(response.responsesmodel) &&
      response.responsesmodel.length > 0 &&
      typeof response.responsesmodel[0] === 'object' &&
      'label' in (response.responsesmodel[0] as RouteItem) &&
      'word' in (response.responsesmodel[0] as RouteItem);

    if (!isModelValid) {
      return `${response.IDsentence},${response.responsesmodel}`;
    }

    const routeModel = (response.responsesmodel as RouteItem[]).sort((a, b) => {
      const order = { DEPART: 1, CORRESPONDANCE: 2, ARRIVEE: 3 };
      return (order[a.label] || 0) - (order[b.label] || 0);
    });

    const cities = routeModel.map((city) => city.word);
    return `${response.IDsentence},${cities.join(',')}`;
  });

  return (
    <div ref={containerRef} className="relative py-8 space-y-16">
      <div className="bg-gray-100 p-4 rounded-lg shadow-lg">
        <h2
          className="text-lg font-bold"
          onClick={() => setShowFormatted((prev) => !prev)}
          style={{ cursor: 'pointer' }}
        >
          Formatted Sentences
        </h2>
        {showFormatted && (
          <div className="space-y-2">
            {formattedResponses.map((formatted, index) => (
              <p key={index} className="text-gray-800">
                {formatted}
              </p>
            ))}
          </div>
        )}
      </div>
      {responses.length > 0 ? (
        responses.map((response, responseIndex) => {
          const isModelValid =
            Array.isArray(response.responsesmodel) &&
            response.responsesmodel.length > 0 &&
            typeof response.responsesmodel[0] === 'object' &&
            'label' in (response.responsesmodel[0] as RouteItem) &&
            'word' in (response.responsesmodel[0] as RouteItem);

          const routeModel = isModelValid
            ? (response.responsesmodel as RouteItem[]).sort((a, b) => {
              const order = { DEPART: 1, CORRESPONDANCE: 2, ARRIVEE: 3 };
              return (order[a.label] || 0) - (order[b.label] || 0);
            })
            : [];

          const errorMessages = !isModelValid
            ? (response.responsesmodel as string[]) || ['Should not be shown']
            : [];

          const isCorrespondance = (city: RouteItem) => city.label === 'CORRESPONDANCE';

          return (
            <div key={responseIndex} className="space-y-8">
              <h2 className="text-xl font-bold">{responseIndex + 1} : ID Sentence {response.IDsentence}</h2>
              <p>"{response.text}"</p>
              {isModelValid ? (
                routeModel.map((city, cityIndex) => (
                  <motion.div
                    key={cityIndex}
                    className="city-container flex items-center gap-4"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: cityIndex * 0.1 }}
                  >
                    <div
                      className={`${isCorrespondance(city) ? 'city-dot-correspondance' : 'city-dot-startOrEnd'}`}
                    />
                    <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4 shadow-lg flex-1">
                      <h3 className="text-lg font-semibold">{city.word}</h3>
                      {city.label === 'DEPART' && (
                        <p className="text-sm text-muted-foreground">Starting Point</p>
                      )}
                      {city.label === 'CORRESPONDANCE' && (
                        <p className="text-sm text-muted-foreground">Via</p>
                      )}
                      {city.label === 'ARRIVEE' && (
                        <p className="text-sm text-muted-foreground">Destination</p>
                      )}
                    </div>
                  </motion.div>
                ))
              ) : hasInteracted ? (
                <div className="bg-red-100 p-4 rounded-lg shadow-md">
                  <h3 className="text-lg font-semibold text-red-600">Errors Detected</h3>
                  <ul className="list-disc pl-5 space-y-2">
                    {errorMessages.map((error, errorIndex) => (
                      <li key={errorIndex} className="text-red-500">
                        {error}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div></div>
              )}
            </div>
          );
        })
      ) : (
        <div></div>
      )}
    </div>
  );
};

export default RouteDisplay;
