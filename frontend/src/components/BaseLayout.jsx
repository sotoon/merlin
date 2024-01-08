import React, { useContext } from "react";
import { AppBar, Toolbar, Typography, Container, Button } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { UserContext } from "../contexts/UserContext";
import PropTypes from "prop-types";

const BaseLayout = ({ children }) => {
  const { user } = useContext(UserContext);

  return (
    <>
      <AppBar
        position="sticky"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
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
            <Typography variant="subtitle1">
              Welcome, {user.username}
            </Typography>
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
      <Container>{children}</Container>
    </>
  );
};

BaseLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default BaseLayout;
