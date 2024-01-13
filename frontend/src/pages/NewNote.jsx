import React from "react";
import { Typography } from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";

const NewNote = () => (
  <DashboardLayout>
    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
      New Note
    </Typography>
  </DashboardLayout>
);

export default NewNote;
