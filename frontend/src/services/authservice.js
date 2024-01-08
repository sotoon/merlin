import API from "./api";

export const signupService = async (userData) => {
  try {
    const response = await API.post("/signup/", userData);
    return response;
  } catch (error) {
    console.error(error);
  }
};

export const loginService = async (userData) => {
  try {
    const response = await API.post("/login/", userData);
    return response;
  } catch (error) {
    console.error(error);
  }
};

export const exchangeCodeForToken = async (code) => {
  try {
    const response = await API.post("/bepa-callback/", { code });
    return response;
  } catch (error) {
    console.error(error);
  }
};
