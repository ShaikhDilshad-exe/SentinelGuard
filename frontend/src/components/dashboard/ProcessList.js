import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Paper, Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { getProcesses } from '../../services/api';

export default function ProcessList() {
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProcesses = async () => {
      try {
        const response = await getProcesses();
        const data = response?.data || response;
        const processList = response.processes || [];

        if (processList.length > 0) {
          const topProcesses = processList
            .sort((a, b) => parseFloat(b.cpu_percent) - parseFloat(a.cpu_percent))
            .slice(0, 10)
            .map(p => ({
              name: p.name.length > 15 ? p.name.substring(0, 15) + '...' : p.name,
              cpu: parseFloat(p.cpu_percent),
              memory: parseFloat(p.memory_percent),
              fullName: p.name,
              pid: p.pid,
            }));
          setProcesses(topProcesses);
        } else {
          setProcesses([]);
        }
        setLoading(false);
      } catch (err) {
        console.error('Error fetching processes:', err);
        setError('Failed to fetch process data');
        setLoading(false);
      }
    };

    fetchProcesses();
    const interval = setInterval(fetchProcesses, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" sx={{ mb: 2, color: '#bb86fc', fontWeight: 'bold' }}>
        Top Processes by CPU Usage
      </Typography>
      {loading ? (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
          <Typography>Loading processes...</Typography>
        </Box>
      ) : error ? (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
          <Typography color="error">{error}</Typography>
        </Box>
      ) : processes.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={processes}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-15} textAnchor="end" height={80} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #bb86fc' }} />
            <Legend />
            <Bar dataKey="cpu" fill="#bb86fc" name="CPU %" />
            <Bar dataKey="memory" fill="#03dac6" name="Memory %" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
          <Typography>No process data available</Typography>
        </Box>
      )}

      {/* Table view below chart */}
      {processes.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, color: '#03dac6' }}>
            Process Details
          </Typography>
          <TableContainer sx={{ maxHeight: 250 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow sx={{ backgroundColor: '#1e1e1e' }}>
                  <TableCell sx={{ color: '#bb86fc' }}>Process Name</TableCell>
                  <TableCell align="right" sx={{ color: '#bb86fc' }}>CPU %</TableCell>
                  <TableCell align="right" sx={{ color: '#bb86fc' }}>Memory %</TableCell>
                  <TableCell align="right" sx={{ color: '#bb86fc' }}>PID</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {processes.map((proc) => (
                  <TableRow key={proc.pid} hover sx={{ '&:hover': { backgroundColor: '#262626' } }}>
                    <TableCell title={proc.fullName}>{proc.fullName}</TableCell>
                    <TableCell align="right">{proc.cpu.toFixed(2)}%</TableCell>
                    <TableCell align="right">{proc.memory.toFixed(2)}%</TableCell>
                    <TableCell align="right">{proc.pid}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}
    </Paper>
  );
}
