import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { RouteResponse, RouteItem } from '@/types';

interface RouteDisplayProps {
  responses: RouteResponse[];
  hasInteracted: boolean;
}

const RouteDisplay: React.FC<RouteDisplayProps> = ({ responses, hasInteracted }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      const cityElements = containerRef.current.querySelectorAll('.city-container');
      cityElements.forEach((city, index) => {
        if (index < cityElements.length - 1) {
          const currentCity = city.getBoundingClientRect();
          const nextCity = cityElements[index + 1].getBoundingClientRect();
          const line = document.createElement('div');
          line.className = 'route-line';
          line.style.height = `${nextCity.top - currentCity.top}px`;
          line.style.left = `${currentCity.left + currentCity.width / 2}px`;
          line.style.top = `${currentCity.top + currentCity.height / 2}px`;
          containerRef.current?.appendChild(line);
        }
      });
    }

    return () => {
      const lines = document.querySelectorAll('.route-line');
      lines.forEach(line => line.remove());
    };
  }, [responses]);

  // Ensure responses is valid before accessing properties.
  const isModelValid = Array.isArray(responses.responsesmodel) &&
    responses.responsesmodel.length > 0 &&
    typeof responses.responsesmodel[0] === "object" &&
    "label" in (responses.responsesmodel[0] as RouteItem) &&
    "word" in (responses.responsesmodel[0] as RouteItem);

  const routeModel = isModelValid
    ? (responses.responsesmodel as RouteItem[]).sort((a, b) => {
      const order = { DEPART: 1, CORRESPONDANCE: 2, ARRIVEE: 3 };
      return (order[a.label] || 0) - (order[b.label] || 0);
    })
    : [];

  const errorMessages = !isModelValid
    ? (responses.responsesmodel as string[]) || ["Should not be shown"]
    : [];

  return (
    <div ref={containerRef} className="relative py-8 space-y-16">
      {isModelValid ? (
        // Display valid routes
        routeModel.map((city, index) => (
          <motion.div
            key={index}
            className="city-container flex items-center gap-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className={`city-dot ${index === 0 ? "start" : index === routeModel.length - 1 ? "end" : ""}`} />
            <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4 shadow-lg flex-1">
              <h3 className="text-lg font-semibold">{city.word}</h3>
              {city.label === "DEPART" && <p className="text-sm text-muted-foreground">Starting Point</p>}
              {city.label === "CORRESPONDANCE" && <p className="text-sm text-muted-foreground">Via</p>}
              {city.label === "ARRIVEE" && <p className="text-sm text-muted-foreground">Destination</p>}
            </div>
          </motion.div>
        ))
      ) : hasInteracted ? (
        // Display errors when data is invalid
        <div className="bg-red-100 p-4 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-red-600">Errors Detected</h3>
          <ul className="list-disc pl-5 space-y-2">
            {errorMessages.map((error, index) => (
              <li key={index} className="text-red-500">
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
};

export default RouteDisplay;
