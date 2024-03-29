import React, { useContext, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import HowToRegSharpIcon from "@mui/icons-material/HowToRegSharp";
import { Button, TextField, Typography } from "@mui/material";

import CentralizedPaper from "../components/CentralizedPaper";
import { AlertContext } from "../contexts/AlertContext";
import { UserContext } from "../contexts/UserContext";
import { signupService } from "../services/authservice";

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const { user } = useContext(UserContext);
  const { setAlert } = useContext(AlertContext);
  const navigate = useNavigate();

  if (user) {
    return <Navigate to="/dashboard" />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    try {
      const userData = { name, email, password };
      await signupService(userData);
      navigate("/login");
    } catch (error) {
      setAlert({ message: "ثبت نام ناموفق، دوباره تلاش کنید!", type: "error" });
    }
  };

  return (
    <CentralizedPaper>
      <Typography component="h1" variant="h5">
        ثبت نام
      </Typography>
      <form onSubmit={handleSubmit} noValidate dir="ltr">
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          label="name"
          autoComplete="name"
          autoFocus
          value={name}
          onChange={(e) => setName(e.target.value)}
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
          ثبت نام
        </Button>
      </form>
    </CentralizedPaper>
  );
};

export default Signup;
