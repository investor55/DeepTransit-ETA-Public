import React, { useState } from 'react';
import { Clock } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import _ from 'lodash';

const ListHeading = ({ heading, subHeading, endEnhancer, maxLines = 1 }) => (
  <div className="sticky left-0 flex items-center justify-between p-4 bg-white border-b border-gray-200 z-10">
    <div className="flex-1 min-w-0">
      <h3 className={`text-lg font-semibold text-gray-900 ${maxLines === 1 ? 'truncate' : ''}`}>
        {heading}
      </h3>
      {subHeading && (
        <p className={`text-sm text-gray-500 ${maxLines === 1 ? 'truncate' : ''}`}>
          {subHeading}
        </p>
      )}
    </div>
    {endEnhancer && (
      <div className="ml-4 flex-shrink-0">
        {endEnhancer()}
      </div>
    )}
  </div>
);

const formatTime = (hour, minute) => {
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
};

const generateDayDistribution = (pattern) => {
  const minutes = _.range(0, 24 * 60, 5);
  
  return minutes.map(minute => {
    const hour = Math.floor(minute / 60);
    const min = minute % 60;
    let density = 0;
    
    switch(pattern) {
      case 'commuter':
        density = 
          Math.exp(-(Math.pow(hour - 8, 2) / 1.5)) * 1.2 +
          Math.exp(-(Math.pow(hour - 17.5, 2) / 1.5)) * 1.2 +
          0.2;
        break;
      case 'express':
        density = (minute % 120 < 15) ? 1 : 0.15;
        break;
      case 'regular':
        density = 
          0.6 + 
          Math.exp(-(Math.pow(hour - 12, 2) / 6)) * 0.4 +
          Math.exp(-(Math.pow(hour - 15, 2) / 8)) * 0.3;
        break;
      default:
        density = 0.5;
    }
    
    return {
      time: formatTime(hour, min),
      minute,
      density: Math.max(0.1, Math.min(1, density + Math.random() * 0.05))
    };
  });
};

const RouteListItem = ({ route, isSelected, onClick }) => {
  const currentTime = new Date();
  const currentMinute = currentTime.getHours() * 60 + currentTime.getMinutes();
  
  const nextArrivals = route.distribution
    .filter(d => d.minute > currentMinute)
    .slice(0, 3)
    .map(d => d.time);

  return (
    <div 
      className={`group cursor-pointer border-b border-gray-200 ${
        isSelected ? 'bg-blue-50' : 'hover:bg-gray-50'
      }`}
      onClick={() => onClick(route)}
    >
      <div className="sticky left-0 bg-inherit z-10 border-r border-gray-200">
        <ListHeading
          heading={`Route ${route.number}`}
          subHeading={route.destination}
          endEnhancer={() => (
            <div className="flex space-x-4">
              {nextArrivals.map((time, index) => (
                <div key={index} className="text-center">
                  <span className="block text-xl font-semibold text-gray-600">
                    {time}
                  </span>
                </div>
              ))}
            </div>
          )}
        />
      </div>
      
      <div className="relative px-4 pb-6">
        <div className="h-40 w-[4320px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={route.distribution}>
              <XAxis 
                dataKey="time"
                interval={11}
                tick={{ fontSize: 12 }}
                padding={{ left: 20, right: 20 }}
              />
              <YAxis hide />
              <Area
                type="monotone"
                dataKey="density"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        <div 
          className="absolute top-0 bottom-8 w-0.5 bg-red-500"
          style={{ 
            left: `${(currentMinute / (24 * 60)) * 4320}px`,
            pointerEvents: 'none'
          }}
        />
      </div>
    </div>
  );
};

const Button = ({ children, variant, size, className }) => (
  <button className={`inline-flex items-center px-3 py-1 border rounded-full ${className}`}>
    {children}
  </button>
);

const ArrivalPanel = () => {
  const busRoutes = [
    {
      id: 1,
      number: "42",
      destination: "Downtown Express",
      color: "blue",
      distribution: generateDayDistribution('commuter')
    },
    {
      id: 2,
      number: "15",
      destination: "Airport Express",
      color: "purple",
      distribution: generateDayDistribution('express')
    },
    {
      id: 3,
      number: "87",
      destination: "University",
      color: "green",
      distribution: generateDayDistribution('regular')
    }
  ];

  const [selectedRoute, setSelectedRoute] = useState(busRoutes[0]);

  return (
    <div className="h-screen overflow-hidden bg-white">
      <div className="sticky top-0 left-0 z-20 bg-white border-b border-gray-200">
        <ListHeading
          heading="Bus Arrivals"
          subHeading="Central Station • Stop #1234"
          endEnhancer={() => (
            <Button variant="outline" size="sm" className="rounded-full">
              <Clock className="h-4 w-4 mr-2" />
              Live
            </Button>
          )}
        />
      </div>

      <div className="h-[calc(100vh-73px)] overflow-x-auto overflow-y-auto">
        {busRoutes.map(route => (
          <RouteListItem
            key={route.id}
            route={route}
            isSelected={route.id === selectedRoute.id}
            onClick={setSelectedRoute}
          />
        ))}
      </div>
    </div>
  );
};

export default ArrivalPanel; 