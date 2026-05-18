import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import LiveAlerts from '../components/LiveAlerts';
import { createTestAlert } from '../services/api';

const AlertsPage = () => {

  const handleCreateTestAlert = async () => {
    try {
      console.log("📡 Sending test alert request...");
      await createTestAlert();
    } catch (error) {
      console.error("❌ Failed to trigger alert:", error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          mb: 3
        }}
      >
        <Typography variant="h4">
          Live Alerts
        </Typography>

        <Button
          variant="contained"
          onClick={handleCreateTestAlert}
        >
          Create Test Alert
        </Button>
      </Box>

      <LiveAlerts />
    </Box>
  );
};

export default AlertsPage;