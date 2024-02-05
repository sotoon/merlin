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
import DashboardLayout from "./components/DashboardLayout";
import { CssBaseline } from "@mui/material";
import { UserProvider } from "./contexts/UserContext";
import { AlertProvider } from "./contexts/AlertContext";
import AlertSnackbar from "./components/AlertSnackbar";
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
      <AlertProvider>
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
                    <DashboardLayout>
                      <Navigate to="/notes?noteType=Goal" />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/notes"
                  element={
                    <DashboardLayout>
                      <NotesPage key="notes" />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/note/:noteId?"
                  element={
                    <DashboardLayout>
                      <NotePage />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <DashboardLayout>
                      <ProfilePage />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/my-team"
                  element={
                    <DashboardLayout>
                      <MyTeamPage />
                    </DashboardLayout>
                  }
                />
              </Routes>
            </BaseLayout>
          </Router>
        </ThemeProvider>
        <AlertSnackbar />
      </AlertProvider>
    </UserProvider>
  );
}

export default App;
