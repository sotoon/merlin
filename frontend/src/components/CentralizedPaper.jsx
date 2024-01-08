import React from "react";
import { Grid, Paper } from "@mui/material";

const CentralizedPaper = ({ children }) => {
    return (
        <Grid container align="center" justifyContent="center" style={{minHeight: '90vh' }}>
            <Grid item xs={12} sm={6} md={4} margin="auto">
                <Paper style={{ padding: '20px' }}>
                    {children}
                </Paper>
            </Grid>
        </Grid>
    )
}

export default CentralizedPaper;