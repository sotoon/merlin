import React, { useContext } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Button,
  IconButton,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { UserContext } from "../contexts/UserContext";
import useAuth from "../hooks/useAuth";
import PropTypes from "prop-types";
import PowerSettingsNewSharpIcon from "@mui/icons-material/PowerSettingsNewSharp";

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
                Welcome, {user.username}
              </Typography>
              <IconButton aria-label="logout" onClick={handleLogout}>
                <PowerSettingsNewSharpIcon color="inherit" fontSize="large" />
              </IconButton>
            </>
          ) : (
            <>
              <Button color="inherit" component={RouterLink} to="/login">
                Login
              </Button>
              <Button color="inherit" component={RouterLink} to="/signup">
                Signup
              </Button>
            </>
          )}
        </Toolbar>
      </AppBar>
      <Container
        sx={{ display: "flex", flexDirection: "column", height: "100vh" }}
      >
        {children}
      </Container>
    </>
  );
};

BaseLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default BaseLayout;
