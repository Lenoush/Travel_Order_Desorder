import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';


interface RouteResponse {
  responsesmodel: Array<JSON>;
  text: string;
}

interface RouteDisplayProps {
  responses: RouteResponse[];
}

const RouteDisplay: React.FC<RouteDisplayProps> = ({ responses }) => {
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

  const routeModel = responses.responsesmodel || [] ;

  return (
    <div ref={containerRef} className="relative py-8 space-y-16">

      {routeModel.map((city, index) => (
        <motion.div
          key={index}
          className="city-container flex items-center gap-4"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
        >

          <div className={`city-dot ${index === 0 ? 'start' : index === routeModel.length - 1 ? 'end' : ''}`} />
          <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4 shadow-lg flex-1">
            <h3 className="text-lg font-semibold">{city.word}</h3>
            {city.label === "DEPART" && <p className="text-sm text-muted-foreground">Starting Point</p>}
            {city.label === "CORRESPONDANCE" && <p className="text-sm text-muted-foreground">Via</p>}
            {city.label === "ARRIVEE" && <p className="text-sm text-muted-foreground">Destination</p>}
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default RouteDisplay;