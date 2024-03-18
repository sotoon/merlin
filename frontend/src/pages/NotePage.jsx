import React, { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";

import FeedbackForm from "../components/FeedbackForm";
import FeedbackList from "../components/FeedbackList";
import Loading from "../components/Loading";
import NoteForm from "../components/NoteForm";
import SummaryForm from "../components/SummaryForm";
import useFetchData from "../hooks/useFetchData";
import { getNote, markNoteAsRead } from "../services/noteservice";

const NotePage = () => {
  const { noteId } = useParams();
  const [searchParams] = useSearchParams();
  const noteType = searchParams.get("noteType") || "";
  const [noteData, setNoteData] = useState({
    title: "",
    content: "",
    date: "",
    type: noteType,
    owner_name: "",
    access_level: {
      can_view: false,
      can_edit: false,
      can_write_summary: false,
      can_write_feedback: false,
    },
  });
  const isLoading = useFetchData(
    () => (noteId ? getNote(noteId) : null),
    setNoteData,
    [noteId],
  );
  useEffect(() => {
    if (noteId) {
      markNoteAsRead(noteId);
    }
  }, [noteId, noteData]);

  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }

  return (
    <>
      <NoteForm
        isReadOnly={noteId ? !noteData.access_level.can_edit : false}
        noteData={noteData}
        noteId={noteId}
        defaultNoteType={noteType}
      />
      {noteId && (
        <SummaryForm
          noteId={noteId}
          summary={noteData.summary}
          isReadOnly={noteId ? !noteData.access_level.can_write_summary : true}
          noteType={noteData.type}
        />
      )}
      {noteId &&
        (noteId ? noteData.access_level.can_write_feedback : false) && (
          <FeedbackForm noteId={noteId} />
        )}
      {noteId && <FeedbackList noteId={noteId} />}
    </>
  );
};

export default NotePage;
