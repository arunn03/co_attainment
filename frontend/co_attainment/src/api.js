import axios from "axios";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "./constant";
import { jwtDecode } from "jwt-decode";

const client = axios.create({
  baseURL: process.env.REACT_APP_ENDPOINT_URL,
});

export const refreshToken = async () => {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN);
  try {
    const res = await axios.post(
      `${process.env.REACT_APP_ENDPOINT_URL}/auth/token/refresh/`,
      { refresh: refreshToken }
    );
    if (res.status === 200) {
      localStorage.setItem(ACCESS_TOKEN, res.data.access);
    } else {
      localStorage.clear();
    }
  } catch (err) {
    console.log(err);
    localStorage.clear();
  }
};

client.interceptors.request.use(
  async (config) => {
    var token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
      const decoded = jwtDecode(token);
      const expirationTime = decoded.exp;
      const now = Date.now() / 1000;

      if (now > expirationTime) {
        await refreshToken();
        token = localStorage.getItem(ACCESS_TOKEN);
      }
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default client;
