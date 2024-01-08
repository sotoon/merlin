// ErrorSnackbar.js
import React, { useContext } from "react";
import { Snackbar, Alert } from "@mui/material";
import { ErrorContext } from "../contexts/ErrorContext";

const ErrorSnackbar = () => {
  const { errorMessage, setErrorMessage } = useContext(ErrorContext);

  const handleClose = () => {
    setErrorMessage("");
  };

  return (
    <Snackbar
      open={!!errorMessage}
      autoHideDuration={6000}
      onClose={handleClose}
    >
      <Alert onClose={handleClose} severity="error" sx={{ width: "100%" }}>
        {errorMessage}
      </Alert>
    </Snackbar>
  );
};

export default ErrorSnackbar;
