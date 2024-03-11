import React, { useContext, useState } from "react";

import { Button, TextField } from "@mui/material";
import { PropTypes } from "prop-types";

import { AlertContext } from "../contexts/AlertContext";
import { UserContext } from "../contexts/UserContext";
import useFetchData from "../hooks/useFetchData";
import { createFeedback, getUserFeedbacks } from "../services/noteservice";
import Loading from "./Loading";
import SectionTitle from "./SectionTitle";

const FeedbackForm = ({ noteId }) => {
  const [feedbackContent, setFeedbackContent] = useState("");
  const { user } = useContext(UserContext);
  const isLoading = useFetchData(
    () => (noteId ? getUserFeedbacks(noteId, user.email) : null),
    (response) =>
      setFeedbackContent(response.length > 0 ? response[0].content : ""),
    [noteId],
  );

  const { setAlert } = useContext(AlertContext);
  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    try {
      await createFeedback(feedbackContent, noteId);
      setAlert({
        message: "فیدبک با موفقیت افزوده شد!",
        type: "success",
      });
    } catch (error) {
      setAlert({
        message: "Something went wrong. Please try again later.",
        type: "error",
      });
    }
  };
  if (isLoading) {
    return <Loading description="در حال دریافت اطلاعات..." />;
  }
  return (
    <>
      <SectionTitle title="نوشتن فیدبک" />
      <form onSubmit={handleFeedbackSubmit}>
        <TextField
          label="فیدبک"
          name="feedback"
          value={feedbackContent}
          placeholder="نوشتن فیدبک"
          onChange={(e) => setFeedbackContent(e.target.value)}
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
