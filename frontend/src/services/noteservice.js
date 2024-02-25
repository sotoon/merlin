import { apiCall } from "./api";

export const createNote = async (noteData) => {
  return await apiCall("post", "/notes/", noteData);
};

export const getNotes = async (noteType, userEmail, retrieve_mentions) => {
  let url = noteType ? `/notes/?type=${noteType}` : "/notes/";
  if (userEmail) {
    url += url.includes("?") ? `&user=${userEmail}` : `?user=${userEmail}`;
  }
  if (retrieve_mentions) {
    url += url.includes("?")
      ? `&retrieve_mentions=${retrieve_mentions}`
      : `?retrieve_mentions=${retrieve_mentions}`;
  }
  return await apiCall("get", url);
};

export const getNote = async (id) => {
  return await apiCall("get", `/notes/${id}/`);
};

export const updateNote = async (noteData, uuid) => {
  return await apiCall("put", `/notes/${uuid}/`, noteData);
};

export const deleteNote = async (uuid) => {
  return await apiCall("delete", `/notes/${uuid}/`);
};

export const createFeedback = async (feedbackContent, noteUUid) => {
  return await apiCall("post", `/notes/${noteUUid}/feedbacks/`, {
    content: feedbackContent,
  });
};

export const getFeedbacks = async (noteUUid) => {
  return await apiCall("get", `/notes/${noteUUid}/feedbacks/`);
};

export const updateSummary = async (summary, noteUUid) => {
  return await apiCall("patch", `/notes/${noteUUid}/`, {
    summary: summary,
  });
};
