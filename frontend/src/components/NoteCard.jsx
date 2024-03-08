import React, { useContext } from "react";
import { useNavigate } from "react-router";
import { Link as RouterLink } from "react-router-dom";

import DeleteIcon from "@mui/icons-material/Delete";
import {
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Divider,
  IconButton,
  Typography,
} from "@mui/material";
import { marked } from "marked";
import PropTypes from "prop-types";

import { AlertContext } from "../contexts/AlertContext";
import { deleteNote } from "../services/noteservice";

const NoteCard = ({ uuid, title, body, date, isReadOnly, ownerName }) => {
  const { setAlert } = useContext(AlertContext);
  const navigate = useNavigate();
  const removeMarkdown = (markdownText) => {
    return marked(markdownText).replace(/<\/?[^>]+(>|$)/g, "\n");
  };

  const handleDelete = (event) => {
    event.preventDefault();
    event.stopPropagation();
    const deleteCurrentNote = async () => {
      try {
        await deleteNote(uuid);
        navigate(0);
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
      }
    };
    deleteCurrentNote();
  };

  return (
    <RouterLink
      to={`/note/${uuid}`}
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
            تاریخ: {date} {ownerName && `,نویسنده: ${ownerName}`}
          </Typography>
          {!isReadOnly && (
            <IconButton
              color="inherit"
              onClick={(event) => handleDelete(event)}
              sx={{
                "&:hover": {
                  color: "#FF9800",
                },
              }}
            >
              <DeleteIcon />
            </IconButton>
          )}
        </CardActions>
      </Card>
    </RouterLink>
  );
};

NoteCard.propTypes = {
  uuid: PropTypes.string,
  title: PropTypes.string,
  body: PropTypes.string,
  date: PropTypes.string,
  isReadOnly: PropTypes.bool,
  ownerName: PropTypes.string,
};

NoteCard.defaultProps = {
  uuid: "",
  title: "",
  body: "",
  data: "",
  isReadOnly: false,
  ownerName: "",
};

export default NoteCard;
