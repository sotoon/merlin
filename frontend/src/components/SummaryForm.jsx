import React, { useContext, useState } from "react";

import { Button, TextField } from "@mui/material";
import { PropTypes } from "prop-types";

import { AlertContext } from "../contexts/AlertContext";
import { updateSummary } from "../services/noteservice";
import SectionTitle from "./SectionTitle";

const VALID_NOTE_TYPES = ["Proposal", "Goal"];

const SummaryForm = ({ noteId, summary, isReadOnly, noteType }) => {
  const [summaryContent, setSummaryContent] = useState(summary);
  const { setAlert } = useContext(AlertContext);
  const handleSummarySubmit = async (e) => {
    e.preventDefault();
    try {
      await updateSummary(summaryContent, noteId);
      setAlert({
        message: "جمع‌بندی با موفقیت افزوده شد!",
        type: "success",
      });
    } catch (error) {
      setAlert({
        message: "Something went wrong. Please try again later.",
        type: "error",
      });
    }
  };
  if (!VALID_NOTE_TYPES.includes(noteType)) {
    return <></>;
  }
  return (
    <>
      <SectionTitle title="جمع‌بندی" />
      <form onSubmit={handleSummarySubmit}>
        <TextField
          label="جمع‌بندی"
          name="summary"
          value={summaryContent}
          placeholder="جمع‌بندی"
          onChange={(e) => setSummaryContent(e.target.value)}
          multiline
          fullWidth
          rows={4}
          margin="normal"
          sx={{
            mb: 2,
          }}
          InputProps={{
            readOnly: isReadOnly,
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
        {!isReadOnly && (
          <Button
            type="submit"
            variant="contained"
            color="primary"
            sx={{ display: "flex" }}
          >
            نوشتن جمع‌بندی
          </Button>
        )}
      </form>
    </>
  );
};

SummaryForm.propTypes = {
  noteId: PropTypes.string,
  summary: PropTypes.string,
  isReadOnly: PropTypes.bool,
  noteType: PropTypes.string,
};

SummaryForm.defaultProps = {
  noteId: "",
  summary: "",
  isReadOnly: true,
  noteType: "",
};

export default SummaryForm;
