import React, { useState, useEffect } from 'react';
import { getNetworkConnections } from '../services/api';
import { Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';

const NetworkPage = () => {
  const [connections, setConnections] = useState([]);

  useEffect(() => {
    const fetchConnections = async () => {
      try {
        const response = await getNetworkConnections();
        //console.log("Full API Response:", response);
        setConnections(response);
      } catch (error) {
        console.error("Error fetching network connections:", error);
      }
    };
    fetchConnections();
    const interval = setInterval(fetchConnections, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <Typography variant="h4" gutterBottom>Active Network Connections</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Local Address</TableCell>
              <TableCell>Remote Address</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>PID</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {connections?.map((conn, index) => (
              <TableRow key={index}>
                <TableCell>{conn.laddr}</TableCell>
                <TableCell>{conn.raddr}</TableCell>
                <TableCell>{conn.status}</TableCell>
                <TableCell>{conn.pid}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default NetworkPage;
