import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Paper, Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { getNetworkConnections } from '../../services/api';

export default function NetworkActivityLog() {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const fetchConnections = async () => {
      try {
        const response = await getNetworkConnections();
        
        // Updated: The API returns the list directly or nested in .connections
        const connectionsArray = Array.isArray(response) ? response : response?.connections || [];

        if (connectionsArray.length > 0) {
          setConnections(connectionsArray.slice(0, 15)); // Show latest 15 connections

          const statusCounts = {};
          connectionsArray.forEach(conn => {
            const status = conn.status || 'ESTABLISHED';
            statusCounts[status] = (statusCounts[status] || 0) + 1;
          });

          const chartPoints = Object.keys(statusCounts).map(status => ({
            name: status,
            count: statusCounts[status],
          }));
          setChartData(chartPoints);
          setError(null); // Clear error on success
        } else {
          setConnections([]);
          setChartData([]);
        }
      } catch (err) {
        console.error('Error fetching network connections:', err);
        setError('Failed to fetch network data');
      } finally {
        setLoading(false);
      }
    };

    fetchConnections();
    const interval = setInterval(fetchConnections, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    const statusMap = {
      'ESTABLISHED': '#03dac6',
      'LISTEN': '#bb86fc',
      'TIME_WAIT': '#ff6b6b',
      'CLOSE_WAIT': '#ffa500',
    };
    return statusMap[status] || '#999';
  };

  return (
    <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" sx={{ mb: 2, color: '#bb86fc', fontWeight: 'bold' }}>
        Network Activity Log
      </Typography>
      
      {loading && connections.length === 0 ? (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
          <Typography>Loading network data...</Typography>
        </Box>
      ) : error ? (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
          <Typography color="error">{error}</Typography>
        </Box>
      ) : connections.length > 0 ? (
        <>
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" sx={{ color: '#999' }}>
              Connections by Status
            </Typography>
            <ResponsiveContainer width="100%" height={150}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #bb86fc' }} />
                <Area type="monotone" dataKey="count" fill="#bb86fc" stroke="#03dac6" />
              </AreaChart>
            </ResponsiveContainer>
          </Box>

          <Typography variant="subtitle2" sx={{ mb: 1, color: '#03dac6' }}>
            Recent Connections
          </Typography>
          <TableContainer sx={{ maxHeight: 300, flex: 1 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow sx={{ backgroundColor: '#1e1e1e' }}>
                  <TableCell sx={{ color: '#bb86fc' }}>Destination IP</TableCell>
                  <TableCell sx={{ color: '#bb86fc' }}>Port</TableCell>
                  <TableCell sx={{ color: '#bb86fc' }}>Status</TableCell>
                  <TableCell align="right" sx={{ color: '#bb86fc' }}>PID</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
  {connections.map((conn, idx) => (
    <TableRow key={idx} hover sx={{ '&:hover': { backgroundColor: '#262626' } }}>
      <TableCell sx={{ fontSize: '0.85rem' }}>
        {/* Changed from laddr to destination_ip */}
        {conn.destination_ip || 'Internal'} 
      </TableCell>
      <TableCell sx={{ fontSize: '0.85rem' }}>
        {/* Changed from raddr to port */}
        {conn.port || 'N/A'}
      </TableCell>
      <TableCell>
        <Chip 
          label={conn.status || 'ESTABLISHED'} 
          size="small"
          sx={{ 
            backgroundColor: getStatusColor(conn.status),
            color: '#000',
            fontSize: '0.75rem',
          }} 
        />
      </TableCell>
      <TableCell align="right">{conn.pid || 'N/A'}</TableCell>
    </TableRow>
  ))}
</TableBody>
            </Table>
          </TableContainer>
        </>
      ) : (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
          <Typography>No network connections available</Typography>
        </Box>
      )}
    </Paper>
  );
}