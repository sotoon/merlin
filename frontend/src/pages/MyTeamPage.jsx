import React, { useState, useEffect, useContext } from "react";
import { Typography, Grid, Divider } from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";
import Loading from "../components/Loading";
import { getMyTeam } from "../services/teamservice";
import { ErrorContext } from "../contexts/ErrorContext";
import MemberCard from "../components/MemberCard";

const MyTeamPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [team, setTeam] = useState([]);
  const { setErrorMessage } = useContext(ErrorContext);

  useEffect(() => {
    const fetchTeamData = async () => {
      try {
        const response = await getMyTeam();
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setTeam(response.data);
      } catch (error) {
        console.error(error);
        setErrorMessage("A Problem occurred. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchTeamData();
  }, []);

  if (isLoading) {
    return (
      <DashboardLayout>
        <Loading description={"در حال دریافت اطلاعات"} />
      </DashboardLayout>
    );
  }

  return (
    <>
      <Typography variant="h4">تیم من</Typography>
      <Divider sx={{ mb: 2, mt: 2 }} />
      <Grid container spacing={2}>
        {team.map((user, index) => (
          <>
            <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
              <MemberCard
                name={user.name}
                email={user.email}
                team={user.team}
              />
            </Grid>
          </>
        ))}
      </Grid>
    </>
  );
};

export default MyTeamPage;
