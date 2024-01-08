import React from "react";
import { Drawer, List, ListItem, ListItemText, Toolbar } from "@mui/material";
import { Container } from "@mui/system";
import PropTypes from "prop-types";

const drawerWidth = 240;

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
          <ListItem button>
            <ListItemText primary="Option 1" />
          </ListItem>
          <ListItem button>
            <ListItemText primary="Option 2" />
          </ListItem>
          <ListItem button>
            <ListItemText primary="Option 3" />
          </ListItem>
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
