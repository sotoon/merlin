import React, { createContext, useState } from "react";

import PropTypes from "prop-types";

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthCheckComplete, setIsAuthCheckComplete] = useState(false);
  const [userTeam, setUserTeam] = useState({});

  return (
    <UserContext.Provider
      value={{
        user,
        setUser,
        isAuthCheckComplete,
        setIsAuthCheckComplete,
        userTeam,
        setUserTeam,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

UserProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
