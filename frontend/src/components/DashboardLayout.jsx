import React from "react";
import {
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
} from "@mui/material";
import { Container } from "@mui/system";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";

const drawerWidth = 240;
const drawerOptions = [
  {
    text: "Goals",
    link: "/goals",
  },
  {
    text: "Meeting Notes",
    link: "/meeting-notes",
  },
  {
    text: "Personal Notes",
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
      </Drawer>
      <Container>
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
