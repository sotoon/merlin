import React from "react";
import { Link as RouterLink } from "react-router-dom";
import {
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Typography,
  Divider,
} from "@mui/material";
import PropTypes from "prop-types";

const MemberCard = ({ username, name, email }) => {
  return (
    <RouterLink
      to={`/notes?user=${username}`}
      component="div"
      style={{ textDecoration: "none", color: "inherit" }}
    >
      <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
        <CardHeader
          title={<Typography variant="h6">{username}</Typography>}
          sx={{ backgroundColor: "#0D47A1", color: "#FFFFFF" }}
        />
        <Divider />
        <CardContent sx={{ flex: "1 0 auto" }}>
          <Typography
            variant="body"
            color="textSecondary"
            component="div"
            sx={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {name}
          </Typography>
        </CardContent>
        <CardActions
          sx={{ marginTop: "auto", justifyContent: "flex-end" }}
          disableSpacing
        >
          <Typography variant="caption" color="textSecondary" sx={{ flex: 1 }}>
            {email}
          </Typography>
        </CardActions>
      </Card>
    </RouterLink>
  );
};

MemberCard.propTypes = {
  name: PropTypes.string,
  username: PropTypes.string,
  email: PropTypes.string,
};

export default MemberCard;