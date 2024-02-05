import React, { useState, useEffect, useContext } from "react";
import {
  TextField,
  Button,
  Typography,
  Divider,
  Card,
  CardHeader,
  CardContent,
  Grid,
} from "@mui/material";
import { getNote, createFeedback, getFeedbacks } from "../services/noteservice";
import { useParams, useNavigate } from "react-router-dom";
import Loading from "../components/Loading";
import { AlertContext } from "../contexts/AlertContext";
import { UserContext } from "../contexts/UserContext";
import SectionTitle from "../components/SectionTitle";
import NoteForm from "../components/NoteForm";
import useFetchData from "../hooks/useFetchData";

const NotePage = () => {
  const { noteId } = useParams();
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [newFeedbackContent, setNewFeedbackContent] = useState("");
  const [feedbacks, setFeedbacks] = useState([]);
  const [noteData, setNoteData] = useState({
    title: "",
    content: "",
    date: "",
    type: "",
    owner: "",
    mentioned_users: [],
  });
  const navigate = useNavigate();
  const { setAlert } = useContext(AlertContext);
  const { user } = useContext(UserContext);
  const isLoading = useFetchData(
    () => (noteId ? getNote(noteId) : null),
    setNoteData,
    [noteId],
  );
  useEffect(() => {
    const fetchNoteFeedbacks = async () => {
      try {
        const response = await getFeedbacks(noteId);
        setFeedbacks(response);
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
      }
    };
    if (noteId) {
      if (noteData.owner !== user.email) {
        setIsReadOnly(true);
      } else {
        setIsReadOnly(false);
        fetchNoteFeedbacks();
      }
    }
  }, [noteId, noteData]);

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

  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }

  return (
    <>
      <NoteForm isReadOnly={isReadOnly} noteData={noteData} noteId={noteId} />
      {isReadOnly && (
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
              Submit
            </Button>
          </form>
        </>
      )}
      {!isReadOnly && (
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
                      <Typography variant="h6">
                        {feedback.owner_name}
                      </Typography>
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
      )}
    </>
  );
};

export default NotePage;
