import { useEffect, useContext } from "react";
import { UserContext } from "../contexts/UserContext";
import { verifyToken } from "../services/authservice";
import { useNavigate } from "react-router-dom";

const useAuth = () => {
  const { setUser, setIsAuthCheckComplete } = useContext(UserContext);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("accessToken");
      if (token) {
        try {
          const user = await verifyToken(token);
          console.log(`verify token resp: ${JSON.stringify(user)}`);
          setUser(user);
        } catch (error) {
          localStorage.clear();
          setUser(null);
          navigate("/login");
        }
      }
      setIsAuthCheckComplete(true);
    };

    checkAuth();
  }, [setUser, setIsAuthCheckComplete]);

  return null;
};

export default useAuth;
