import React, { useState } from "react";
import { Grid } from "@mui/material";
import Loading from "../components/Loading";
import { getMyTeam } from "../services/teamservice";
import MemberCard from "../components/MemberCard";
import useFetchData from "../hooks/useFetchData";
import SectionTitle from "../components/SectionTitle";

const MyTeamPage = () => {
  const [team, setTeam] = useState([]);
  const isLoading = useFetchData(getMyTeam, setTeam, []);
  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }

  return (
    <>
      <SectionTitle title={"تیم من"} />
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
