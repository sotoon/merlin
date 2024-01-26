import React from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import BepaCallback from "./pages/BepaCallback";
import NotesPage from "./pages/NotesPage";
import BaseLayout from "./components/BaseLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import { CssBaseline } from "@mui/material";
import { UserProvider } from "./contexts/UserContext";
import { ErrorProvider } from "./contexts/ErrorContext";
import ErrorSnackbar from "./components/ErrorSnackbar";
import "./App.css";
import NotePage from "./pages/NotePage";
import ProfilePage from "./pages/ProfilePage";
import MyTeamPage from "./pages/MyTeamPage";

const theme = createTheme({
  palette: {
    background: {
      default: "#ECECEC", // Light gray background
      paper: "#FFFFFF", // White paper background
    },
    primary: {
      main: "#2196F3", // Classic Blue
    },
    secondary: {
      main: "#FF9800", // Orange
    },
    mode: "light",
  },
  typography: {
    fontFamily: "iranyekanwebregular, sans-serif",
  },
});

function App() {
  return (
    <UserProvider>
      <ErrorProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <BaseLayout>
              <Routes>
                <Route exact path="/" element={<Navigate to="/login" />} />
                <Route path="/login" Component={Login} />
                {process.env.REACT_APP_SIGNUP_DISABLED !== "true" && (
                  <Route path="/signup" Component={Signup} />
                )}
                <Route path="/bepa-callback" Component={BepaCallback} />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Navigate to="/notes?noteType=Goal" />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/notes"
                  element={
                    <ProtectedRoute>
                      <NotesPage key="notes" />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/note/:noteId?"
                  element={
                    <ProtectedRoute>
                      <NotePage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <ProfilePage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/my-team"
                  element={
                    <ProtectedRoute>
                      <MyTeamPage />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </BaseLayout>
          </Router>
        </ThemeProvider>
        <ErrorSnackbar />
      </ErrorProvider>
    </UserProvider>
  );
}

export default App;
