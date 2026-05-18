import React, { useState, useEffect } from 'react';
import { getProcesses } from '../services/api';
import { Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';

const ProcessesPage = () => {
  const [processes, setProcesses] = useState([]);

  useEffect(() => {
    const fetchProcesses = async () => {
      try {
        const response = await getProcesses();
        
        console.log("Raw Process Data:", response); // Let's log it just in case!

        // If it's an array directly (like the Network page)
        if (Array.isArray(response)) {
            setProcesses(response);
        } 
        // If the backend wraps it in an object like { processes: [...] }
        else if (response && Array.isArray(response.processes)) {
            setProcesses(response.processes);
        }

      } catch (error) {
        console.error("Error fetching processes:", error);
      }
    };
    fetchProcesses();
  }, []);

  return (
    <div>
      <Typography variant="h4" gutterBottom>Running Processes</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>PID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>CPU %</TableCell>
              <TableCell>Memory %</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {/* Added the safety question mark here! */}
            {processes?.map((proc) => (
              <TableRow key={proc.pid}>
                <TableCell>{proc.pid}</TableCell>
                <TableCell>{proc.name}</TableCell>
                <TableCell>{proc.username}</TableCell>
                {/* Rounding these numbers so they look clean on the dashboard */}
                <TableCell>{proc.cpu_percent?.toFixed(2)}%</TableCell>
                <TableCell>{proc.memory_percent?.toFixed(2)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default ProcessesPage;