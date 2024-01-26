import API from "./api";

export const signupService = async (userData) => {
  try {
    const response = await API.post("/signup/", userData);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const loginService = async (userData) => {
  try {
    const response = await API.post("/login/", userData);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const exchangeCodeForToken = async (code) => {
  try {
    const response = await API.get(`/bepa-callback?code=${code}`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const refreshToken = async () => {
  const refreshToken = localStorage.getItem("refreshToken");
  try {
    const response = await API.post("/login/refresh/", {
      refresh: refreshToken,
    });
    localStorage.setItem("accessToken", response.data.access);
    return response.data.access;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const verifyToken = async (token) => {
  const response = await API.post("/verify-token/", { token });
  return response.data;
};

export const getProfileData = async () => {
  const response = await API.get("/profile/");
  return response;
};

export const updateProfile = async (profileData) => {
  const response = await API.patch("/profile/", profileData);
  return response;
};
