import { apiCall } from "./api";

export const getMyTeam = async () => {
  return await apiCall("get", "/my-team/");
};

export const getAllUsers = async () => {
  return await apiCall("get", "/users/");
};
