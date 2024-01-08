import React, { useState, useContext } from "react";
import { loginService } from "../services/authservice";
import CentralizedPaper from "../components/CentralizedPaper";
import { TextField, Button, Typography } from "@mui/material";
import PowerSharp from "@mui/icons-material/PowerSharp";
import LockOpenSharp from "@mui/icons-material/LockOpenSharp";
import { useNavigate, Navigate } from "react-router-dom";
import { UserContext } from "../contexts/UserContext";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { user, setUser } = useContext(UserContext);
  const navigate = useNavigate();

  if (user) {
    return <Navigate to="/dashboard" />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const userData = { email, password };
      const response = await loginService(userData);
      console.log(
        `response status: ${response.status} response data: ${JSON.stringify(
          response.data,
        )}`,
      );
      localStorage.setItem("accessToken", response.data.tokens.access);
      localStorage.setItem("refreshToken", response.data.tokens.refresh);
      const user = {
        username: response.data.username,
        email: response.data.email,
      };
      setUser(user);
      const { from } = location.state || { from: { pathname: "/" } };
      navigate(from);
    } catch (error) {
      console.error(error);
    }
  };

  const handleBepaLogin = () => {
    const baseAuthUrl = process.env.REACT_APP_BEPA_AUTH_URL;
    const clientId = process.env.REACT_APP_CLIENT_ID;
    const callbackUrl = process.env.REACT_APP_BEPA_CALLBACK_URL;
    const bepaAuthUrl = `${baseAuthUrl}?client_id=${clientId}&redirect_uri=${callbackUrl}&response_type=code`;
    window.location.href = bepaAuthUrl;
  };

  return (
    <CentralizedPaper>
      <Typography component="h1" variant="h5">
        Sign in
      </Typography>
      <Button
        type="button"
        fullWidth
        margin="normal"
        variant="contained"
        color="secondary"
        onClick={handleBepaLogin}
        sx={{ mt: 2, mb: 1 }}
        startIcon={<PowerSharp />}
      >
        Login with Bepa
      </Button>
      <form onSubmit={handleSubmit} noValidate>
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          label="Email Address"
          autoComplete="email"
          autoFocus
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          label="Password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          startIcon={<LockOpenSharp />}
        >
          Sign In
        </Button>
      </form>
    </CentralizedPaper>
  );
};

export default Login;
