import React, { useState, useEffect, useContext } from "react";
import { Typography, Grid, Divider } from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";
import Loading from "../components/Loading";
import { getMyTeams } from "../services/teamservice";
import { ErrorContext } from "../contexts/ErrorContext";
import MemberCard from "../components/MemberCard";

const MyTeamPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [teams, setTeams] = useState([]);
  const { setErrorMessage } = useContext(ErrorContext);

  useEffect(() => {
    const fetchTeamsData = async () => {
      try {
        const response = await getMyTeams();
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setTeams(response.data);
      } catch (error) {
        console.error(error);
        setErrorMessage("A Problem occurred. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchTeamsData();
  }, []);

  if (isLoading) {
    return (
      <DashboardLayout>
        <Loading description={"در حال دریافت اطلاعات"} />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Typography variant="h4">تیم من</Typography>
      <Divider sx={{ mb: 2, mt: 2 }} />
      {teams.map((team, index) => (
        <>
          <Typography variant="h5" key={index}>
            تیم {team.name}
          </Typography>
          <Grid container spacing={2} key={index}>
            {team.user_set.map((user, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <MemberCard
                  username={user.username}
                  name={user.name}
                  email={user.email}
                />
              </Grid>
            ))}
          </Grid>
        </>
      ))}
    </DashboardLayout>
  );
};

export default MyTeamPage;
