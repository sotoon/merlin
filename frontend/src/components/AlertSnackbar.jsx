import React, { useContext } from "react";

import { Alert, Snackbar } from "@mui/material";

import { AlertContext } from "../contexts/AlertContext";

const AlertSnackbar = () => {
  const { alert, setAlert } = useContext(AlertContext);

  const handleClose = () => {
    setAlert({ message: "", type: "error" });
  };

  return (
    <Snackbar
      open={!!alert.message}
      autoHideDuration={6000}
      onClose={handleClose}
    >
      <Alert onClose={handleClose} severity={alert.type} sx={{ width: "100%" }}>
        {alert.message}
      </Alert>
    </Snackbar>
  );
};

export default AlertSnackbar;
