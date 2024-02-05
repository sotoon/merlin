import React, { useContext, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import Loading from "../components/Loading";
import { AlertContext } from "../contexts/AlertContext";
import { exchangeCodeForToken } from "../services/authservice";

const BepaCallback = () => {
  const location = useLocation();
  const { setAlert } = useContext(AlertContext);
  const navigate = useNavigate();

  useEffect(() => {
    const parseQuery = (queryString) => {
      const query = {};
      new URLSearchParams(queryString).forEach((value, key) => {
        query[key] = value;
      });
      return query;
    };

    const { code, state } = parseQuery(location.search);

    const storedStateValue = sessionStorage.getItem("stateValue");

    if (!storedStateValue || !state || storedStateValue !== state) {
      console.error("Invalid State!");
      setAlert({ message: "Couldn't connect to bepa!", type: "error" });
      navigate("/login");
      return;
    }

    if (code) {
      exchangeCodeForToken(code)
        .then((response) => {
          localStorage.setItem("accessToken", response.access);
          localStorage.setItem("refreshToken", response.refresh);
          navigate("/dashboard");
        })
        .catch(() => {
          setAlert({ message: "Couldn't connect to bepa!", type: "error" });
          navigate("/login");
        });
    } else {
      navigate("/login");
    }
  }, [location, navigate]);

  return <Loading description="Connecting to Bepa..." />;
};

export default BepaCallback;
