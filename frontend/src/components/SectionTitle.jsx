import React from "react";
import { Typography, Divider } from "@mui/material";
import propTypes from "prop-types";

const SectionTitle = ({ title }) => {
  return (
    <>
      <Typography variant="h4" sx={{ mt: 2 }}>
        {title}
      </Typography>
      <Divider sx={{ mb: 2, mt: 2 }} />
    </>
  );
};

SectionTitle.propTypes = {
  title: propTypes.string,
};

export default SectionTitle;
