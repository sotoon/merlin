import React, { createContext, useState } from "react";
import PropTypes from "prop-types";

export const AlertContext = createContext({
  alert: {
    message: "",
    type: "error",
  },
  setAlert: () => {},
});

export const AlertProvider = ({ children }) => {
  const [alert, setAlert] = useState({ message: "", type: "error" });

  return (
    <AlertContext.Provider value={{ alert, setAlert }}>
      {children}
    </AlertContext.Provider>
  );
};

AlertProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
