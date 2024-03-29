import { useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { jwtDecode } from "jwt-decode";

import { AlertContext } from "../contexts/AlertContext";
import { UserContext } from "../contexts/UserContext";
import { verifyToken } from "../services/authservice";
import { getMyTeam } from "../services/teamservice";

const useAuth = () => {
  const { user, setUser, setIsAuthCheckComplete, setUserTeam } =
    useContext(UserContext);
  const { setAlert } = useContext(AlertContext);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("accessToken");
      if (token) {
        try {
          const payload = jwtDecode(token);
          if (payload.name && payload.email) {
            setUser({
              name: payload.name,
              email: payload.email,
            });
          } else {
            const user = await verifyToken(token);
            setUser(user);
          }
        } catch (error) {
          localStorage.clear();
          setUser(null);
          navigate("/login");
        }
      }
      setIsAuthCheckComplete(true);
    };
    checkAuth();
  }, [setUser, setIsAuthCheckComplete, localStorage.getItem("accessToken")]);

  useEffect(() => {
    const getUserTeam = async () => {
      if (user) {
        try {
          const response = await getMyTeam();
          setUserTeam(response);
        } catch (error) {
          setAlert({
            message: "Couldn't check team status!",
            type: "error",
          });
        }
      }
    };
    getUserTeam();
  }, [user]);

  return null;
};

export default useAuth;
