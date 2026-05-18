import React, { useState, useEffect } from 'react';

import {
  List,
  ListItem,
  ListItemText,
  Paper,
  Chip,
  Box
} from '@mui/material';

const LiveAlerts = () => {

  const [alerts, setAlerts] = useState([]);

  // =====================================================
  // FETCH ALERTS EVERY 2 SECONDS
  // =====================================================
  useEffect(() => {

    const fetchAlerts = async () => {

      try {

        const response = await fetch(
          "http://127.0.0.1:8000/api/alerts"
        );

        const data = await response.json();

        console.log("📡 ALERT API RESPONSE:", data);

        if (data.alerts) {

          // Sort newest alerts first
          const sortedAlerts = [...data.alerts].sort(
            (a, b) => b.timestamp - a.timestamp
          );

          setAlerts(sortedAlerts);

        }

      } catch (error) {

        console.error(
          "❌ Failed to fetch alerts:",
          error
        );

      }
    };

    // Initial fetch
    fetchAlerts();

    // Poll every 2 seconds
    const interval = setInterval(fetchAlerts, 2000);

    return () => clearInterval(interval);

  }, []);

  // =====================================================
  // ALERT CHIP COLORS
  // =====================================================
  const getSeverityChip = (severity) => {

    let color = "default";

    if (severity === "CRITICAL") color = "error";
    else if (severity === "HIGH") color = "warning";
    else if (severity === "MEDIUM") color = "info";
    else if (severity === "LOW") color = "default";

    return (
      <Chip
        label={severity}
        color={color}
        size="small"
        sx={{ mr: 1 }}
      />
    );
  };

  // =====================================================
  // UI
  // =====================================================
  return (

    <Paper
      sx={{
        backgroundColor: "#1e1e1e",
        mt: 2
      }}
    >

      <List>

        {alerts.length === 0 ? (

          <ListItem>

            <ListItemText
              secondary="Waiting for system activity..."
            />

          </ListItem>

        ) : (

          alerts.map((alert, idx) => (

            <ListItem
              key={alert.id || idx}
              divider
            >

              <ListItemText

                primary={
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1
                    }}
                  >

                    {getSeverityChip(alert.severity)}

                    <span>
                      {alert.message}
                    </span>

                  </Box>
                }

                secondary={`Source: ${
                  alert.type || "Heuristic Engine"
                } | ${
                  new Date(
                    alert.timestamp * 1000
                  ).toLocaleTimeString()
                }`}

              />

            </ListItem>

          ))
        )}

      </List>

    </Paper>
  );
};

export default LiveAlerts;