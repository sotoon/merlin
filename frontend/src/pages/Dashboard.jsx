import React from "react";
import { Typography } from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";

const Dashboard = () => (
  <DashboardLayout>
    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
      Hellooooo
    </Typography>
  </DashboardLayout>
);

export default Dashboard;
