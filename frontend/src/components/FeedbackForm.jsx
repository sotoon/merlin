import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button, TextField } from "@mui/material";
import { PropTypes } from "prop-types";

import { AlertContext } from "../contexts/AlertContext";
import { createFeedback } from "../services/noteservice";
import SectionTitle from "./SectionTitle";

const FeedbackForm = ({ noteId }) => {
  const [newFeedbackContent, setNewFeedbackContent] = useState("");
  const navigate = useNavigate();
  const { setAlert } = useContext(AlertContext);
  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    try {
      await createFeedback(newFeedbackContent, noteId);
      navigate(`/dashboard`);
    } catch (error) {
      setAlert({
        message: "Something went wrong. Please try again later.",
        type: "error",
      });
    }
  };
  return (
    <>
      <SectionTitle title="نوشتن فیدبک" />
      <form onSubmit={handleFeedbackSubmit}>
        <TextField
          label="فیدبک"
          name="feedback"
          value={newFeedbackContent}
          placeholder="نوشتن فیدبک"
          onChange={(e) => setNewFeedbackContent(e.target.value)}
          multiline
          fullWidth
          rows={4}
          margin="normal"
          sx={{
            mb: 2,
          }}
          InputProps={{
            style: {
              textAlign: "right",
              direction: "rtl",
            },
          }}
          InputLabelProps={{
            style: {
              textAlign: "right",
              right: 0,
              left: "auto",
              marginRight: 20,
            },
          }}
        />
        <Button
          type="submit"
          variant="contained"
          color="primary"
          sx={{ display: "flex" }}
        >
          ایجاد فیدبک
        </Button>
      </form>
    </>
  );
};

FeedbackForm.propTypes = {
  noteId: PropTypes.string,
};

export default FeedbackForm;
