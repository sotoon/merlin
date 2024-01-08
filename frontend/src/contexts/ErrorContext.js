import React, { createContext, useState } from "react";
import PropTypes from "prop-types";

export const ErrorContext = createContext({
  errorMessage: "",
  setErrorMessage: () => {},
});

export const ErrorProvider = ({ children }) => {
  const [errorMessage, setErrorMessage] = useState("");

  return (
    <ErrorContext.Provider value={{ errorMessage, setErrorMessage }}>
      {children}
    </ErrorContext.Provider>
  );
};

ErrorProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
