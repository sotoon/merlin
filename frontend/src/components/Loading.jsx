import React from "react";
import { CircularProgress, Typography } from "@mui/material";
import CentralizedPaper from "../components/CentralizedPaper";
import PropTypes from "prop-types";

const Loading = ({ description }) => {
  return (
    <CentralizedPaper>
      <CircularProgress color="primary" variant="indeterminate" size={80} />
      <Typography variant="h5" component="h1">
        {description}
      </Typography>
    </CentralizedPaper>
  );
};

Loading.propTypes = {
  description: PropTypes.string,
};

export default Loading;
