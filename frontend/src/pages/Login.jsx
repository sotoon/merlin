import React, { useState, useContext } from "react";
import { loginService } from "../services/authservice";
import CentralizedPaper from "../components/CentralizedPaper";
import { TextField, Button, Typography } from "@mui/material";
import PowerSharp from "@mui/icons-material/PowerSharp";
import LockOpenSharp from "@mui/icons-material/LockOpenSharp";
import { useNavigate, Navigate } from "react-router-dom";
import { UserContext } from "../contexts/UserContext";
import { AlertContext } from "../contexts/AlertContext";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { user, setUser } = useContext(UserContext);
  const { setAlert } = useContext(AlertContext);
  const navigate = useNavigate();

  if (user) {
    return <Navigate to="/dashboard" />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const userData = { email, password };
      const response = await loginService(userData);
      localStorage.setItem("accessToken", response.tokens.access);
      localStorage.setItem("refreshToken", response.tokens.refresh);
      const user = {
        name: response.name,
        email: response.email,
      };
      setUser(user);
      const { from } = location.state || { from: { pathname: "/" } };
      navigate(from);
    } catch (error) {
      setAlert({
        message: "A Problem occurred. Please try again later.",
        type: "error",
      });
    }
  };

  const handleBepaLogin = () => {
    const baseAuthUrl = process.env.REACT_APP_BEPA_AUTH_URL;
    const clientId = encodeURIComponent(process.env.REACT_APP_CLIENT_ID);
    const callbackUrl = encodeURIComponent(
      process.env.REACT_APP_BEPA_CALLBACK_URL,
    );
    const stateValue = Math.random().toString(36).substring(7);
    sessionStorage.setItem("stateValue", stateValue);
    const bepaAuthUrl = `${baseAuthUrl}/?next=/openid-v2/authorize/%3Fclient_id%3D${clientId}%26redirect_uri%3D${callbackUrl}%26response_type%3Dcode%26scope%3Daddress%2Bphone%2Bopenid%2Bprofile%2Bemail%26state%3D${stateValue}%26`;
    window.location.href = bepaAuthUrl;
  };

  return (
    <CentralizedPaper>
      <Typography component="h1" variant="h5">
        ورود به سامانه ارزیابی عملکرد
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
        ورود با بپا
      </Button>
      <form onSubmit={handleSubmit} noValidate dir="ltr">
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
          ورود
        </Button>
      </form>
    </CentralizedPaper>
  );
};

export default Login;
