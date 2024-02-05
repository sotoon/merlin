import React, { useState } from "react";
import { Typography, Grid, Divider } from "@mui/material";
import Loading from "../components/Loading";
import { getMyTeam } from "../services/teamservice";
import MemberCard from "../components/MemberCard";
import useFetchData from "../hooks/useFetchData";

const MyTeamPage = () => {
  const [team, setTeam] = useState([]);
  const isLoading = useFetchData(getMyTeam, setTeam);
  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
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
