import API from "./api";
export const getMyTeam = async () => {
  try {
    const response = await API.get(`/my-team/`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
