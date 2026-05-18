import React from 'react';

import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography
} from '@mui/material';

import { Link } from 'react-router-dom';

import DashboardIcon from '@mui/icons-material/Dashboard';
import SecurityIcon from '@mui/icons-material/Security';
import MemoryIcon from '@mui/icons-material/Memory';
import DnsIcon from '@mui/icons-material/Dns';
import LanIcon from '@mui/icons-material/Lan';
import BugReportIcon from '@mui/icons-material/BugReport';

const drawerWidth = 240;

// ---------------------------------------------------------
// MENU ITEMS
// ---------------------------------------------------------
const menuItems = [

  {
    text: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/'
  },

  {
    text: 'Live Alerts',
    icon: <SecurityIcon />,
    path: '/alerts'
  },

  {
    text: 'Processes',
    icon: <MemoryIcon />,
    path: '/processes'
  },

  {
    text: 'System Activity',
    icon: <DnsIcon />,
    path: '/activity'
  },

  {
    text: 'Network',
    icon: <LanIcon />,
    path: '/network'
  },

  {
    text: 'File Scanner',
    icon: <BugReportIcon />,
    path: '/scanner'
  }

];

// ---------------------------------------------------------
// SIDEBAR COMPONENT
// ---------------------------------------------------------
const Sidebar = () => {

  return (

    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,

        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: '#1e1e1e',
          color: 'white'
        }
      }}
    >

      {/* TITLE */}
      <Typography
        variant="h5"
        sx={{
          p: 2,
          textAlign: 'center',
          fontWeight: 'bold'
        }}
      >
        SentinelGuard
      </Typography>

      {/* MENU */}
      <List>

        {menuItems.map((item) => (

          <ListItem
            key={item.text}
            disablePadding
          >

            <ListItemButton
              component={Link}
              to={item.path}
            >

              <ListItemIcon
                sx={{
                  color: 'white'
                }}
              >
                {item.icon}
              </ListItemIcon>

              <ListItemText
                primary={item.text}
              />

            </ListItemButton>

          </ListItem>

        ))}

      </List>

    </Drawer>
  );
};

export default Sidebar;