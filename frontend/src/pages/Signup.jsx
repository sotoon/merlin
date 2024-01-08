import React, { useState } from "react";
import { signupService } from "../services/authservice";
import { useNavigate } from "react-router-dom";
import { TextField, Button, Typography } from "@mui/material";
import CentralizedPaper from "../components/CentralizedPaper";
import HowToRegSharpIcon from "@mui/icons-material/HowToRegSharp";

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    try {
      const userData = { username, email, password };
      const response = await signupService(userData);
      console.log(
        `response status: ${response.status} response data: ${response.data}`,
      );
      navigate("/login");
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <CentralizedPaper>
      <Typography component="h1" variant="h5">
        Sign up
      </Typography>
      <form onSubmit={handleSubmit} noValidate>
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          label="Username"
          autoComplete="username"
          autoFocus
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          label="Email Address"
          autoComplete="email"
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
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          label="Confirm Password"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          startIcon={<HowToRegSharpIcon />}
        >
          Sign Up
        </Button>
      </form>
    </CentralizedPaper>
  );
};

export default Signup;
