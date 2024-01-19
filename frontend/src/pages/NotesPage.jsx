import React, { useState, useEffect, useContext } from "react";
import { Fab, Typography, Container, Grid, Divider } from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";
import PropTypes from "prop-types";
import AddSharpIcon from "@mui/icons-material/AddSharp";
import NoteCard from "../components/NoteCard";
import Loading from "../components/Loading";
import { getNotes } from "../services/noteservice";
import { Link as RouterLink } from "react-router-dom";
import { ErrorContext } from "../contexts/ErrorContext";

const NoteTypeTitles = {
  Goal: "اهداف",
  Meeting: "جلسات",
  Personal: "شخصی",
};

const NotesPage = ({ noteType }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [notes, setNotes] = useState([]);
  const { setErrorMessage } = useContext(ErrorContext);

  useEffect(() => {
    const fetchNotesData = async () => {
      try {
        const response = await getNotes(noteType);
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setNotes(response.data);
      } catch (error) {
        console.error(error);
        setErrorMessage("A Problem occurred. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchNotesData();
  }, []);

  if (isLoading) {
    return (
      <DashboardLayout>
        <Loading description={"در حال دریافت اطلاعات"} />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Container>
        <Typography variant="h4">
          یادداشت‌های {NoteTypeTitles[noteType]}
        </Typography>
        <Divider sx={{ mb: 2, mt: 2 }} />
        <Grid container spacing={2}>
          {notes.map((note, index) => (
            <Grid item xs={12} sm={12} md={12} key={index}>
              <NoteCard
                id={note.id}
                title={note.title}
                body={note.content}
                date={note.date}
              />
            </Grid>
          ))}
        </Grid>
      </Container>
      <RouterLink to="/notes">
        <Fab
          color="secondary"
          aria-label="Add Note"
          sx={{
            position: "fixed",
            bottom: (theme) => theme.spacing(10),
            left: (theme) => theme.spacing(10),
            transform: "scale(1.2)",
          }}
        >
          <AddSharpIcon sx={{ transform: "scale(1.4)" }} />
        </Fab>
      </RouterLink>
    </DashboardLayout>
  );
};

NotesPage.propTypes = {
  noteType: PropTypes.string.isRequired,
};

export default NotesPage;
