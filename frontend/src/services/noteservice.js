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

export const getNotes = async (noteType) => {
  try {
    const response = await API.get(`/notes?type=${noteType}`);
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

export const updateNote = async (noteData, id) => {
  try {
    const response = await API.put(`/notes/${id}/`, noteData);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
