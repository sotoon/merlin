import React, { useContext } from "react";
import { Navigate } from "react-router-dom";
import { UserContext } from "../contexts/UserContext";
import Loading from "../components/Loading";

// eslint-disable-next-line react/prop-types
const ProtectedRoute = ({ children }) => {
  const { user, isAuthCheckComplete } = useContext(UserContext);
  if (!isAuthCheckComplete) {
    return <Loading description="" />;
  }
  if (!user) {
    return <Navigate to="/login" />;
  }
  return children;
};

export default ProtectedRoute;
