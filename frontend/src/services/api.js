import axios from "axios";
import { refreshToken } from "./authservice";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;
      try {
        const newAccessToken = await refreshToken();
        originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
        return API(originalRequest);
      } catch (refreshError) {
        localStorage.clear();
        window.location.href = "/login";
      }
    }
    // eslint-disable-next-line no-undef
    return Promise.reject(error);
  },
);

export const apiCall = async (method, url, data) => {
  try {
    const response = await API[method](url, data);
    console.log(
      `response status: ${response.status} response data: ${JSON.stringify(
        response.data,
      )}`,
    );
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

export default API;
