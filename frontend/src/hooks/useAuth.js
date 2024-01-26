import { useEffect, useContext } from "react";
import { UserContext } from "../contexts/UserContext";
import { jwtDecode } from "jwt-decode";
import { verifyToken } from "../services/authservice";
import { useNavigate } from "react-router-dom";
import { getMyTeams } from "../services/teamservice";

const useAuth = () => {
  const { user, setUser, setIsAuthCheckComplete, setIsLeader } =
    useContext(UserContext);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("accessToken");
      if (token) {
        try {
          const payload = jwtDecode(token);
          if (payload.username && payload.email) {
            setUser({
              username: payload.username,
              email: payload.email,
            });
          } else {
            const user = await verifyToken(token);
            console.log(`verify token resp: ${JSON.stringify(user)}`);
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
    const checkIsLeader = async () => {
      if (user) {
        try {
          const response = await getMyTeams();
          if (response.data.length > 0) {
            setIsLeader(true);
          }
        } catch (error) {
          console.error(error);
        }
      }
    };
    checkIsLeader();
  }, [user]);

  return null;
};

export default useAuth;
