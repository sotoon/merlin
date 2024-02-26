import React, { useState } from "react";
import { Link as RouterLink, useSearchParams } from "react-router-dom";

import AddSharpIcon from "@mui/icons-material/AddSharp";
import { Fab, Grid } from "@mui/material";

import Loading from "../components/Loading";
import NoteCard from "../components/NoteCard";
import SectionTitle from "../components/SectionTitle";
import useFetchData from "../hooks/useFetchData";
import { getNotes } from "../services/noteservice";

const NoteTypeTitles = {
  Goal: "اهداف",
  Meeting: "جلسات",
  Personal: "شخصی",
  Task: "فعالیت‌ها",
  Proposal: "پروپوزال‌ها",
  Message: "پیام‌ها",
  Template: "قالب‌ها",
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
    [noteType, userEmail, retrieve_mentions],
  );

  let pageTitle = `یادداشت‌ها${noteType ? "ی" : ""} ${
    NoteTypeTitles[noteType]
  }`;
  if (userName) {
    pageTitle += `از کاربر ${userName}`;
  }
  if (retrieve_mentions) {
    pageTitle = "پیام‌ها";
  }

  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
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
      <RouterLink to={noteType ? `/note?noteType=${noteType}` : "/note"}>
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
