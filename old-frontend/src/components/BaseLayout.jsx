import React, { useContext } from "react";
import { Link as RouterLink } from "react-router-dom";

import PowerSettingsNewSharpIcon from "@mui/icons-material/PowerSettingsNewSharp";
import {
  AppBar,
  Box,
  Button,
  IconButton,
  Toolbar,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";

import { UserContext } from "../contexts/UserContext";
import useAuth from "../hooks/useAuth";

const BaseLayout = ({ children }) => {
  useAuth();
  const { user, setUser } = useContext(UserContext);

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
  };

  return (
    <>
      <AppBar
        position="sticky"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar color="primary">
          <Typography
            variant="h6"
            noWrap
            component="a"
            href="/"
            flexGrow={1}
            textDecoration="none"
            sx={{
              mr: 2,
              display: { xs: "none", md: "flex" },
              fontFamily: "monospace",
              fontWeight: 700,
              letterSpacing: ".3rem",
              color: "white",
              textDecoration: "none",
            }}
          >
            Merlin
          </Typography>
          {user ? (
            <>
              <Typography variant="subtitle1">
                خوش آمدید, {user.name}
              </Typography>
              <IconButton aria-label="logout" onClick={handleLogout}>
                <PowerSettingsNewSharpIcon color="inherit" fontSize="large" />
              </IconButton>
            </>
          ) : (
            <>
              <Button color="inherit" component={RouterLink} to="/login">
                ورود
              </Button>
              {process.env.REACT_APP_SIGNUP_DISABLED !== "true" && (
                <Button color="inherit" component={RouterLink} to="/signup">
                  ثبت‌نام
                </Button>
              )}
            </>
          )}
        </Toolbar>
      </AppBar>
      <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
        {children}
      </Box>
    </>
  );
};

BaseLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default BaseLayout;
