import React, { useState } from 'react';
import { loginService } from "../services/authservice";
import CentralizedPaper from "../components/CentralizedPaper";
import { TextField, Button, Typography } from '@mui/material';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const userData = { email, password };
      const response = await loginService(userData);
      console.log(`response status: ${response.status} response data: ${response.data}`);
      localStorage.setItem('token', response.data.tokens.access);
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
  }

  return (
    <CentralizedPaper>
      <Typography component="h1" variant="h5">
        Sign in
      </Typography>
      <Button
        type="button"
        fullWidth
        variant='contained'
        color="primary"
        onClick={handleBepaLogin}>
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
        >
          Sign In
        </Button>
      </form>
    </CentralizedPaper>
  );
};

export default Login;
