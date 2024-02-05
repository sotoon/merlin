import { apiCall } from "./api";

export const signupService = async (userData) => {
  return await apiCall("post", "/signup/", userData);
};

export const loginService = async (userData) => {
  return await apiCall("post", "/login/", userData);
};

export const exchangeCodeForToken = async (code) => {
  return await apiCall("get", "/bepa-callback?code=" + code);
};

export const refreshToken = async () => {
  const refreshToken = localStorage.getItem("refreshToken");
  const response = await apiCall("post", "/login/refresh", {
    refresh: refreshToken,
  });
  localStorage.setItem("accessToken", response.access);
  return response.access;
};

export const verifyToken = async (token) => {
  return await apiCall("post", "/verify-token/", { token });
};

export const getProfileData = async () => {
  return await apiCall("get", "/profile/");
};

export const updateProfile = async (profileData) => {
  return await apiCall("patch", "/profile/", profileData);
};
