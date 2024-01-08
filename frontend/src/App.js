import React from 'react';
import { ThemeProvider, createTheme} from '@mui/material/styles';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import BepaCallback from './pages/BepaCallback';
import Home from './pages/Home';
import Layout from "./components/Layout";
import './App.css';

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Layout>
          <Routes>
            <Route exact path='/' Component={Home}/>
            <Route path='/login' Component={Login}/>
            <Route path='/signup' Component={Signup}/>
            <Route path="/bepa-callback" Component={BepaCallback} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
