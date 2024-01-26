import React from "react";
import {
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
  Typography,
  Box,
} from "@mui/material";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";

const drawerWidth = 240;
const noteOptions = [
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

const personalOptions = [
  {
    text: "👤 پروفایل",
    link: "/profile",
  },
];

const DashboardLayout = ({ children }) => {
  return (
    <Box
      sx={{
        display: "flex",
        width: "100%",
      }}
    >
      <Box sx={{ flexShrink: 0 }}>
        <Drawer
          variant="permanent"
          anchor="right"
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
          <Typography
            component="h1"
            variant="h6"
            sx={{ mt: 2, mb: 0.5, ml: 1 }}
          >
            یادداشت‌ها
          </Typography>
          <Divider />
          <List>
            {noteOptions.map((noteOption) => (
              <ListItemButton
                key={noteOption.text}
                component={RouterLink}
                to={noteOption.link}
              >
                <ListItemText
                  primary={noteOption.text}
                  sx={{ textAlign: "right" }}
                />
              </ListItemButton>
            ))}
          </List>
          <Typography
            component="h1"
            variant="h6"
            sx={{ mt: 2, mb: 0.5, ml: 1 }}
          >
            شخصی
          </Typography>
          <Divider />
          <List>
            {personalOptions.map((drawerOption) => (
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
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: `100%`,
          marginRight: 0,
          p: 3,
          maxWidth: "1200px",
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

DashboardLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default DashboardLayout;
