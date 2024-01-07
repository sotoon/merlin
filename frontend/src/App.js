import React from 'react';
import { ThemeProvider, createTheme} from '@mui/material/styles';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Home from './pages/Home';
import './App.css';

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Routes>
          <Route exact path='/' Component={Home}/>
          <Route path='/login' Component={Login}/>
          <Route path='/signup' Component={Signup}/>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
