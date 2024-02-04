import API from "./api";

export const createNote = async (noteData) => {
  try {
    const response = await API.post("/notes/", noteData);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const getNotes = async (noteType, userEmail, retrieve_mentions) => {
  try {
    let url = noteType ? `/notes/?type=${noteType}` : "/notes/";
    if (userEmail) {
      url += url.includes("?") ? `&user=${userEmail}` : `?user=${userEmail}`;
    }
    if (retrieve_mentions) {
      url += url.includes("?")
        ? `&retrieve_mentions=${retrieve_mentions}`
        : `?retrieve_mentions=${retrieve_mentions}`;
    }
    const response = await API.get(url);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const getNote = async (id) => {
  try {
    const response = await API.get(`/notes/${id}/`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const updateNote = async (noteData, uuid) => {
  try {
    const response = await API.put(`/notes/${uuid}/`, noteData);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const deleteNote = async (uuid) => {
  try {
    const response = await API.delete(`/notes/${uuid}/`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const createFeedback = async (feedbackContent, noteUUid) => {
  try {
    const response = await API.post(`/notes/${noteUUid}/feedbacks/`, {
      content: feedbackContent,
    });
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
