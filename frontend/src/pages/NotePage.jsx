import React, { useState, useEffect, useContext } from "react";
import { getNote } from "../services/noteservice";
import { useParams } from "react-router-dom";
import Loading from "../components/Loading";
import { UserContext } from "../contexts/UserContext";
import NoteForm from "../components/NoteForm";
import useFetchData from "../hooks/useFetchData";
import FeedbackList from "../components/FeedbackList";
import FeedbackForm from "../components/FeedbackForm";

const NotePage = () => {
  const { noteId } = useParams();
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [noteData, setNoteData] = useState({
    title: "",
    content: "",
    date: "",
    type: "",
    owner: "",
    mentioned_users: [],
  });
  const { user } = useContext(UserContext);
  const isLoading = useFetchData(
    () => (noteId ? getNote(noteId) : null),
    setNoteData,
    [noteId],
  );
  useEffect(() => {
    if (noteId) {
      if (noteData.owner !== user.email) {
        setIsReadOnly(true);
      } else {
        setIsReadOnly(false);
      }
    } else {
      setIsReadOnly(false);
    }
  }, [noteId, noteData]);

  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }

  return (
    <>
      <NoteForm isReadOnly={isReadOnly} noteData={noteData} noteId={noteId} />
      {isReadOnly ? (
        <FeedbackForm noteId={noteId} />
      ) : (
        <FeedbackList noteId={noteId} />
      )}
    </>
  );
};

export default NotePage;
