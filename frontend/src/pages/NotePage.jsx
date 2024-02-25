import React, { useContext, useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";

import FeedbackForm from "../components/FeedbackForm";
import FeedbackList from "../components/FeedbackList";
import Loading from "../components/Loading";
import NoteForm from "../components/NoteForm";
import SummaryForm from "../components/SummaryForm";
import { UserContext } from "../contexts/UserContext";
import useFetchData from "../hooks/useFetchData";
import { getNote } from "../services/noteservice";

const NotePage = () => {
  const { noteId } = useParams();
  const [searchParams] = useSearchParams();
  const noteType = searchParams.get("noteType") || "";
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [noteData, setNoteData] = useState({
    title: "",
    content: "",
    date: "",
    type: noteType,
    committee: "",
    owner_name: "",
  });
  const { user, userTeam } = useContext(UserContext);
  const [isLeader, setIsLeader] = useState(false);
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
    for (let i = 0; i < userTeam.length; i++) {
      if (userTeam[i].email == noteData.owner) {
        setIsLeader(true);
      }
    }
  }, [noteId, noteData]);

  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }

  return (
    <>
      <NoteForm
        isReadOnly={isReadOnly}
        noteData={noteData}
        noteId={noteId}
        defaultNoteType={noteType}
      />
      {noteId && (
        <SummaryForm
          noteId={noteId}
          summary={noteData.summary}
          isLeader={isLeader}
          noteType={noteData.type}
        />
      )}
      {noteId && isReadOnly && <FeedbackForm noteId={noteId} />}
      {noteId && <FeedbackList noteId={noteId} />}
    </>
  );
};

export default NotePage;
