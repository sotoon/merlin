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
import { marked } from "marked";
import PropTypes from "prop-types";

const NoteCard = ({ id, title, body, date }) => {
  const removeMarkdown = (markdownText) => {
    return marked(markdownText).replace(/<\/?[^>]+(>|$)/g, "\n"); // Remove HTML tags
  };

  return (
    <RouterLink
      to={`/notes/${id}`}
      component="div"
      style={{ textDecoration: "none", color: "inherit" }}
    >
      <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
        <CardHeader
          title={<Typography variant="h6">{title}</Typography>}
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
            {removeMarkdown(body)}
          </Typography>
        </CardContent>
        <CardActions
          sx={{ marginTop: "auto", justifyContent: "flex-end" }}
          disableSpacing
        >
          <Typography variant="caption" color="textSecondary">
            {date}
          </Typography>
        </CardActions>
      </Card>
    </RouterLink>
  );
};

NoteCard.propTypes = {
  id: PropTypes.number,
  title: PropTypes.string,
  body: PropTypes.string,
  date: PropTypes.string,
};

export default NoteCard;
