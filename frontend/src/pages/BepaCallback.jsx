import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { exchangeCodeForToken } from "../services/authservice";
import Loading from "../components/Loading";

const BepaCallback = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const parseQuery = (queryString) => {
      const query = {};
      new URLSearchParams(queryString).forEach((value, key) => {
        query[key] = value;
      });
      return query;
    };

    const { code } = parseQuery(location.search);

    if (code) {
      exchangeCodeForToken(code)
        .then((response) => {
          localStorage.setItem("accessToken", response.data.access);
          localStorage.setItem("refreshToken", response.data.refresh);
          navigate("/dashboard");
        })
        .catch((error) => {
          console.error("Error exchanging code for token", error);
          navigate("/login");
        });
    } else {
      // navigate('/login');
    }
  }, [location, navigate]);

  return <Loading description="Connecting to Bepa..." />;
};

export default BepaCallback;
