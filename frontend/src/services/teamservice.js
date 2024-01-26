import API from "./api";
export const getMyTeams = async () => {
  try {
    const response = await API.get(`/my-teams/`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
