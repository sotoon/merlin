import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { exchangeCodeForToken } from '../services/authservice';
import { CircularProgress, Typography, Container }  from '@mui/material';

const BepaCallback = () => {
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        const parseQuery = (queryString) => {
            const query = {};
            new URLSearchParams(queryString).forEach((value, key) => {
                query[key] = value;
            });
            return query;
        };

        const { code } = parseQuery(location.search);

        if (code) {
            exchangeCodeForToken(code)
                .then(response => {
                    localStorage.setItem('token', response.data.access);
                    navigate('/dashboard');
                })
                .catch(error => {
                    console.error('Error exchanging code for token', error);
                    navigate('/login');
                });
        } else {
            // navigate('/login');
        }
    }, [location, navigate]);

    return (
        <Container component="main" maxWidth="xs">
            <CircularProgress
                color="primary"
                variant="indeterminate"
                size={80}
            />
            <Typography variant="h5" component="h1">
               Connecting to bepa... 
            </Typography>
        </Container>
    );
};

export default BepaCallback;
