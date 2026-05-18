import React, { useState, useEffect } from 'react';
import { List, ListItem, ListItemText, Paper } from '@mui/material';
import { WS_URL } from '../services/api';

const LiveActivityFeed = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'event') {
        const newEvent = message.payload;
        setEvents((prevEvents) => [newEvent, ...prevEvents].slice(0, 100)); // Keep last 100 events
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };

    return () => {
      ws.close();
    };
  }, []);

  // --- NEW FEATURE: Smart Formatter ---
  // This looks at the event type and extracts only the relevant pieces of info
  const formatDetails = (event) => {
    try {
      // Ensure metadata is a readable object
      const meta = typeof event.metadata === 'string' ? JSON.parse(event.metadata) : (event.metadata || {});

      // Customize the text based on what the engine caught
      if (event.type === 'process') {
        return `Name: ${meta.name} (PID: ${meta.pid}) | CPU: ${meta.cpu_percent?.toFixed(2)}% | RAM: ${meta.memory_percent?.toFixed(2)}%`;
      } 
      else if (event.type === 'network') {
        return `Target IP: ${meta.destination_ip || meta.raddr} | Port: ${meta.destination_port || 'N/A'}`;
      } 
      else if (event.type === 'file') {
        return `Path: ${meta.file_path || 'Unknown'} | Action: ${meta.event_type || 'Modified'}`;
      }
      
      // Fallback: If it's a brand new event type, just show a snippet
      return 'Activity logged successfully.';
      
    } catch (e) {
      return 'Details unavailable';
    }
  };

  return (
    <Paper>
      <List>
        {events.map((event, index) => (
          <ListItem key={index} divider>
            <ListItemText
              primary={`${event.type.toUpperCase()}: Event`}
              // Replace JSON.stringify with our new formatter!
              secondary={`${formatDetails(event)} • ${new Date(event.timestamp * 1000).toLocaleString()}`}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default LiveActivityFeed;