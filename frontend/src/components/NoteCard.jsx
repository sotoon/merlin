import React, { useContext } from "react";
import { Link as RouterLink } from "react-router-dom";
import {
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Typography,
  Divider,
  IconButton,
} from "@mui/material";
import { marked } from "marked";
import DeleteIcon from "@mui/icons-material/Delete";
import { deleteNote } from "../services/noteservice";
import { useNavigate } from "react-router";
import { ErrorContext } from "../contexts/ErrorContext";
import PropTypes from "prop-types";

const NoteCard = ({ id, title, body, date }) => {
  const { setErrorMessage } = useContext(ErrorContext);
  const navigate = useNavigate();
  const removeMarkdown = (markdownText) => {
    return marked(markdownText).replace(/<\/?[^>]+(>|$)/g, "\n"); // Remove HTML tags
  };

  const handleDelete = (event) => {
    event.preventDefault(); // Prevent default action
    event.stopPropagation(); // Stop event propagation
    const deleteCurrentNote = async () => {
      try {
        const response = await deleteNote(id);
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        navigate(0);
      } catch (error) {
        console.error(error);
        setErrorMessage("Something went wrong. Please try again later.");
      }
    };
    deleteCurrentNote();
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
          <Typography variant="caption" color="textSecondary" sx={{ flex: 1 }}>
            {date}
          </Typography>
          <IconButton
            color="inherit"
            onClick={(event) => handleDelete(event)}
            sx={{
              "&:hover": {
                color: "#FF9800", // Change this to the desired hover color
              },
            }}
          >
            <DeleteIcon />
          </IconButton>
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
