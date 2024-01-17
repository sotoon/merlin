import React from "react";
import {
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";
import { Container } from "@mui/system";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";

const drawerWidth = 240;
const drawerOptions = [
  {
    text: "🚀 Goals",
    link: "/goals",
  },
  {
    text: "👥 Meeting Notes",
    link: "/meeting-notes",
  },
  {
    text: "📝 Personal Notes",
    link: "/personal-notes",
  },
];

const DashboardLayout = ({ children }) => {
  return (
    <>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
          },
        }}
      >
        <Toolbar />
        <Typography component="h1" variant="h6" sx={{ mt: 2, mb: 0.5, ml: 1 }}>
          Notes
        </Typography>
        <Divider />
        <List>
          {drawerOptions.map((drawerOption) => (
            <ListItemButton
              key={drawerOption.text}
              components={RouterLink}
              to={drawerOption.link}
            >
              <ListItemText primary={drawerOption.text} />
            </ListItemButton>
          ))}
        </List>
        <Divider />
      </Drawer>
      <Container
        component="main"
        sx={{
          flex: 1,
        }}
      >
        <Toolbar />
        {children}
      </Container>
    </>
  );
};

DashboardLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default DashboardLayout;
