import React from 'react';
import { Typography } from '@mui/material';
import LiveActivityFeed from '../components/LiveActivityFeed';

const SystemActivityPage = () => {
  return (
    <div>
      <Typography variant="h4" gutterBottom>System Activity</Typography>
      <LiveActivityFeed />
    </div>
  );
};

export default SystemActivityPage;
