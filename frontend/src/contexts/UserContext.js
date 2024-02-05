import React, { createContext, useState } from "react";

import PropTypes from "prop-types";

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthCheckComplete, setIsAuthCheckComplete] = useState(false);
  const [isLeader, setIsLeader] = useState(false);

  return (
    <UserContext.Provider
      value={{
        user,
        setUser,
        isAuthCheckComplete,
        setIsAuthCheckComplete,
        isLeader,
        setIsLeader,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

UserProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
