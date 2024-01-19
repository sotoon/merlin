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
    text: "🚀 اهداف",
    link: "/goals",
  },
  {
    text: "👥 جلسات",
    link: "/meeting-notes",
  },
  {
    text: "📝 یادداشت‌های شخصی",
    link: "/personal-notes",
  },
];

const DashboardLayout = ({ children }) => {
  return (
    <>
      <Drawer
        variant="permanent"
        anchor="right"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          right: 0, // Position the drawer on the right
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
          },
        }}
      >
        <Toolbar />
        <Typography component="h1" variant="h6" sx={{ mt: 2, mb: 0.5, ml: 1 }}>
          یادداشت‌ها
        </Typography>
        <Divider />
        <List>
          {drawerOptions.map((drawerOption) => (
            <ListItemButton
              key={drawerOption.text}
              component={RouterLink}
              to={drawerOption.link}
            >
              <ListItemText
                primary={drawerOption.text}
                sx={{ textAlign: "right" }}
              />
            </ListItemButton>
          ))}
        </List>
        <Divider />
      </Drawer>
      <Container
        component="main"
        sx={{
          flex: 1,
          marginLeft: drawerWidth, // Add margin to the main content to avoid overlap
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
