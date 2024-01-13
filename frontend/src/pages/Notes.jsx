import React from "react";
import { Fab, Typography } from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";
import PropTypes from "prop-types";
import AddSharpIcon from "@mui/icons-material/AddSharp";
import { Link as RouterLink } from "react-router-dom";

const Notes = ({ noteType }) => {
  return (
    <DashboardLayout>
      <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
        {noteType}
      </Typography>
      <RouterLink to="/new-note">
        <Fab
          color="secondary"
          aria-label="Add Note"
          sx={{
            position: "fixed",
            bottom: (theme) => theme.spacing(10),
            right: (theme) => theme.spacing(10),
            transform: "scale(1.2)",
          }}
        >
          <AddSharpIcon sx={{ transform: "scale(1.4)" }} />
        </Fab>
      </RouterLink>
    </DashboardLayout>
  );
};

Notes.propTypes = {
  noteType: PropTypes.string.isRequired,
};

export default Notes;
