import React, { useContext, useState } from "react";
import { signupService } from "../services/authservice";
import { useNavigate, Navigate } from "react-router-dom";
import { TextField, Button, Typography } from "@mui/material";
import CentralizedPaper from "../components/CentralizedPaper";
import HowToRegSharpIcon from "@mui/icons-material/HowToRegSharp";
import { UserContext } from "../contexts/UserContext";
import { ErrorContext } from "../contexts/ErrorContext";

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const { user } = useContext(UserContext);
  const { setErrorMessage } = useContext(ErrorContext);
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
      const response = await signupService(userData);
      console.log(
        `response status: ${response.status} response data: ${JSON.stringify(
          response.data,
        )}`,
      );
      navigate("/login");
    } catch (error) {
      console.error(error);
      setErrorMessage("Something went wrong. Please try again later.");
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
