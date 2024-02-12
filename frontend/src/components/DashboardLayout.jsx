import React, { useContext } from "react";
import { Link as RouterLink } from "react-router-dom";

import {
  Box,
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";

import { UserContext } from "../contexts/UserContext";
import ProtectedRoute from "./ProtectedRoute";

const drawerWidth = 240;
const noteOptions = [
  {
    text: "🚀 اهداف",
    link: "/notes?noteType=Goal",
  },
  {
    text: "🤝 جلسات",
    link: "/notes?noteType=Meeting",
  },
  {
    text: "📝 یادداشت‌های شخصی",
    link: "/notes?noteType=Personal",
  },
  {
    text: "🛠️ فعالیت‌ها",
    link: "/notes?noteType=Task",
  },
  {
    text: "📈 پروپوزال",
    link: "/notes?noteType=Proposal",
  },
];

const personalOptions = [
  {
    text: "👤 پروفایل",
    link: "/profile",
    leaderCondition: false,
  },
  {
    text: "👥 تیم من",
    link: "/my-team",
    leaderCondition: true,
  },
  {
    text: "💬 پیام‌ها",
    link: "/notes?retrieve_mentions=true",
    leaderCondition: false,
  },
];

const DashboardLayout = ({ children }) => {
  const { isLeader } = useContext(UserContext);
  return (
    <ProtectedRoute>
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
              {personalOptions.map(
                (drawerOption) =>
                  (!drawerOption.leaderCondition || isLeader) && (
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
                  ),
              )}
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
    </ProtectedRoute>
  );
};

DashboardLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default DashboardLayout;
