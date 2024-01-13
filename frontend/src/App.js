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
import Dashboard from "./pages/Dashboard";
import Notes from "./pages/Notes";
import NewNote from "./pages/NewNote";
import BaseLayout from "./components/BaseLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import { CssBaseline } from "@mui/material";
import { UserProvider } from "./contexts/UserContext";
import { ErrorProvider } from "./contexts/ErrorContext";
import ErrorSnackbar from "./components/ErrorSnackbar";
import "./App.css";

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
    fontFamily: "Roboto, sans-serif",
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
                <Route path="/signup" Component={Signup} />
                <Route path="/bepa-callback" Component={BepaCallback} />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/goals"
                  element={
                    <ProtectedRoute>
                      <Notes noteType="Goal" />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/meeting-notes"
                  element={
                    <ProtectedRoute>
                      <Notes noteType="Meeting" />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/personal-notes"
                  element={
                    <ProtectedRoute>
                      <Notes noteType="Personal" />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/new-note"
                  element={
                    <ProtectedRoute>
                      <NewNote />
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
