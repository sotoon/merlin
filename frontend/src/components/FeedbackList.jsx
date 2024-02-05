import React, { useState } from "react";

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";

import useFetchData from "../hooks/useFetchData";
import { getFeedbacks } from "../services/noteservice";
import Loading from "./Loading";
import SectionTitle from "./SectionTitle";

const FeedbackList = ({ noteId }) => {
  const [feedbacks, setFeedbacks] = useState([]);
  const isLoading = useFetchData(
    () => (noteId ? getFeedbacks(noteId) : null),
    setFeedbacks,
    [noteId],
  );
  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }
  return (
    <>
      <SectionTitle title="فیدبک‌ها" />
      <Grid container spacing={2}>
        {feedbacks.map((feedback, index) => (
          <Grid item xs={12} sm={12} md={12} key={index}>
            <Card
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
              }}
            >
              <CardHeader
                title={
                  <Typography variant="h6">{feedback.owner_name}</Typography>
                }
                sx={{ backgroundColor: "#0D47A1", color: "#FFFFFF" }}
              />
              <Divider />
              <CardContent sx={{ flex: "1 0 auto" }}>
                <Typography
                  variant="body"
                  color="textSecondary"
                  component="div"
                >
                  {feedback.content}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  );
};

FeedbackList.propTypes = {
  noteId: PropTypes.string,
};

export default FeedbackList;
