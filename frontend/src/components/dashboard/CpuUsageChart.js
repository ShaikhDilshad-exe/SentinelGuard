import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Paper, Box, Typography } from '@mui/material';
import { getSystemStats } from '../../services/api';

export default function CpuUsageChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getSystemStats();
        
        // Fixed: Extract cpu_usage from the nested process_monitoring object
        const cpuValue = response.process_monitoring?.cpu_usage || 0;

        if (typeof cpuValue === 'number') {
          setData(prevData => {
            const newData = [...prevData];
            const timestamp = new Date().toLocaleTimeString();
            newData.push({ time: timestamp, cpu: cpuValue });
            if (newData.length > 60) newData.shift();
            return newData;
          });
        }
      } catch (error) {
        console.error('Error fetching CPU data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" sx={{ mb: 2, color: '#bb86fc', fontWeight: 'bold' }}>
        CPU Usage (Last 5 minutes)
      </Typography>
      {!data.length && loading ? (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
          <Typography>Loading CPU data...</Typography>
        </Box>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="time" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
            <Tooltip contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #bb86fc' }} />
            <Line type="monotone" dataKey="cpu" stroke="#bb86fc" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Paper>
  );
}