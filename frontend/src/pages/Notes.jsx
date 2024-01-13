import React from "react";
import { Typography } from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";
import PropTypes from "prop-types";

const Notes = ({ noteType }) => (
  <DashboardLayout>
    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
      {noteType}
    </Typography>
  </DashboardLayout>
);

Notes.propTypes = {
  noteType: PropTypes.string.isRequired,
};

export default Notes;
