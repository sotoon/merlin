import React, { useState, useEffect, useContext } from "react";
import {
  Fab,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
} from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";
import PropTypes from "prop-types";
import AddSharpIcon from "@mui/icons-material/AddSharp";
import { getNotes } from "../services/noteservice";
import { Link as RouterLink } from "react-router-dom";
import { ErrorContext } from "../contexts/ErrorContext";

const NotesPage = ({ noteType }) => {
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
      }
    };
    fetchNotesData();
  }, []);

  return (
    <DashboardLayout>
      <Container>
        <Typography variant="h4">My {noteType} Notes</Typography>
        <Grid container spacing={2}>
          {notes.map((note, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <RouterLink to={`/notes/${note.id}`}>
                <Card
                  sx={{
                    width: "100%",
                    marginBottom: (theme) => theme.spacing(2),
                  }}
                >
                  <CardContent>
                    <Typography variant="body1">{note.title}</Typography>
                  </CardContent>
                </Card>
              </RouterLink>
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

NotesPage.propTypes = {
  noteType: PropTypes.string.isRequired,
};

export default NotesPage;
