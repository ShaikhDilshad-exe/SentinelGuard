import React from 'react';
import { Grid, Container, Box, Typography } from '@mui/material';
import CpuUsageChart from '../components/dashboard/CpuUsageChart';
import ProcessList from '../components/dashboard/ProcessList';
import NetworkActivityLog from '../components/dashboard/NetworkActivityLog';

export default function DashboardPage() {
  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ color: '#bb86fc', fontWeight: 'bold', mb: 1 }}>
          Security Dashboard
        </Typography>
        <Typography variant="body2" sx={{ color: '#999' }}>
          Real-time monitoring and threat detection overview
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* CPU Usage Chart - Full Width */}
        <Grid item xs={12}>
          <CpuUsageChart key="cpu-chart" />
        </Grid>

        {/* Process List - Left Half */}
        <Grid item xs={12} md={6}>
          <ProcessList key="process-list" />
        </Grid>

        {/* Network Activity Log - Right Half */}
        <Grid item xs={12} md={6}>
          <NetworkActivityLog key="network-log" />
        </Grid>
      </Grid>
    </Container>
  );
}
