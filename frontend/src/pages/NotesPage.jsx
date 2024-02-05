import React, { useState } from "react";
import { Fab, Grid } from "@mui/material";
import AddSharpIcon from "@mui/icons-material/AddSharp";
import NoteCard from "../components/NoteCard";
import Loading from "../components/Loading";
import { getNotes } from "../services/noteservice";
import { Link as RouterLink, useSearchParams } from "react-router-dom";
import useFetchData from "../hooks/useFetchData";
import SectionTitle from "../components/SectionTitle";

const NoteTypeTitles = {
  Goal: "اهداف",
  Meeting: "جلسات",
  Personal: "شخصی",
  Task: "فعالیت‌ها",
  "": "",
};

const NotesPage = () => {
  const [searchParams] = useSearchParams();
  const noteType = searchParams.get("noteType") || "";
  const userEmail = searchParams.get("useremail") || "";
  const userName = searchParams.get("username") || "";
  const retrieve_mentions = searchParams.get("retrieve_mentions") || false;
  const areNotesReadOnly = userEmail || retrieve_mentions;
  const [notes, setNotes] = useState([]);
  const isLoading = useFetchData(
    () => getNotes(noteType, userEmail, retrieve_mentions),
    setNotes,
  );
  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }
  let pageTitle = `یادداشت‌ها${noteType ? "ی" : ""} ${
    NoteTypeTitles[noteType]
  }`;
  if (userName) {
    pageTitle += `از کاربر ${userName}`;
  }
  if (retrieve_mentions) {
    pageTitle = "یادداشت‌هایی که در آن‌ها منشن شده‌اید";
  }

  return (
    <>
      <SectionTitle title={pageTitle} />
      <Grid container spacing={2}>
        {notes.map((note, index) => (
          <Grid item xs={12} sm={12} md={12} key={index}>
            <NoteCard
              uuid={note.uuid}
              title={note.title}
              body={note.content}
              date={note.date}
              isReadOnly={areNotesReadOnly}
            />
          </Grid>
        ))}
      </Grid>
      <RouterLink to="/note">
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
    </>
  );
};

export default NotesPage;
