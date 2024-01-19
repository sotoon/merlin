import React, { useContext, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { exchangeCodeForToken } from "../services/authservice";
import { ErrorContext } from "../contexts/ErrorContext";
import Loading from "../components/Loading";

const BepaCallback = () => {
  const location = useLocation();
  const { setErrorMessage } = useContext(ErrorContext);
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
      setErrorMessage("Couldn't connect to bepa!");
      navigate("/login");
      return;
    }

    if (code) {
      exchangeCodeForToken(code)
        .then((response) => {
          localStorage.setItem("accessToken", response.data.access);
          localStorage.setItem("refreshToken", response.data.refresh);
          navigate("/dashboard");
        })
        .catch((error) => {
          console.error("Error exchanging code for token", error);
          setErrorMessage("Couldn't connect to bepa!");
          navigate("/login");
        });
    } else {
      navigate("/login");
    }
  }, [location, navigate]);

  return <Loading description="Connecting to Bepa..." />;
};

export default BepaCallback;
