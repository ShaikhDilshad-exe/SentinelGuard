import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';

// Components & Layout
import Layout from './components/Layout';

// Pages
import DashboardPage from './pages/DashboardPage';
import AlertsPage from './pages/AlertsPage';
import ProcessesPage from './pages/ProcessesPage';
import SystemActivityPage from './pages/SystemActivityPage';
import NetworkPage from './pages/NetworkPage';
import ScannerPage from "./pages/ScannerPage";

// Define the SOC-style Dark Theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      {/* Layout contains the Sidebar and the main content area[cite: 9] */}
      <Layout>
        {/* 
            The Routes component looks at the current URL and renders 
            the matching Route element[cite: 3, 12].
        */}
        <Routes>
          {/* Main Dashboard Overview[cite: 5] */}
          <Route path="/" element={<DashboardPage />} />

          {/* Real-time Security Alerts[cite: 4] */}
          <Route path="/alerts" element={<AlertsPage />} />

          {/* System Process Monitoring[cite: 7] */}
          <Route path="/processes" element={<ProcessesPage />} />

          {/* Live System Activity Feed[cite: 8] */}
          <Route path="/activity" element={<SystemActivityPage />} />

          {/* Active Network Connections[cite: 6] */}
          <Route path="/network" element={<NetworkPage />} />
          <Route path="/scanner" element={<ScannerPage />} />
        </Routes>
      </Layout>
    </ThemeProvider>
  );
}

export default App;