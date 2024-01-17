import React, { useState, useEffect, useContext, useRef } from "react";
import {
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Divider,
} from "@mui/material";
import { createNote, getNote, updateNote } from "../services/noteservice";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import ReactQuill from "react-quill"; // Import the ReactQuill component
import "react-quill/dist/quill.snow.css";
import { ErrorContext } from "../contexts/ErrorContext";

const NotePage = () => {
  const { noteId } = useParams();
  const [formData, setFormData] = useState(() => {
    const savedData = localStorage.getItem("noteFormData");
    return savedData
      ? JSON.parse(savedData)
      : { title: "", content: "", date: "", type: "" };
  });
  const navigate = useNavigate();
  const { setErrorMessage } = useContext(ErrorContext);

  const quillRef = useRef(null);

  useEffect(() => {
    if (quillRef.current) {
      // Access the Quill instance using the ref
      const quill = quillRef.current.getEditor();

      // Set the size to 'large' programmatically
      quill.format("size", "large");
      quill.format("direction", "rtl");
      quill.format("align", "right");
    }
  }, []);

  useEffect(() => {
    const fetchNoteData = async () => {
      try {
        const response = await getNote(noteId);
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setFormData(response.data);
      } catch (error) {
        console.error(error);
        setErrorMessage("Something went wrong. Please try again later.");
      }
    };
    console.debug(`note Id is: ${noteId}`);
    if (noteId) {
      fetchNoteData();
    }
  }, [noteId]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleContentChange = (value) => {
    setFormData({
      ...formData,
      content: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (noteId) {
        const response = await updateNote(formData, noteId);
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
      } else {
        const response = await createNote(formData);
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
      }
      navigate("/dashboard");
    } catch (error) {
      console.error(error);
      setErrorMessage("Something went wrong. Please try again later.");
    }
  };

  useEffect(() => {
    if (!noteId) {
      localStorage.setItem("noteFormData", JSON.stringify(formData));
    }
  }, [formData]);

  return (
    <DashboardLayout>
      <Typography variant="h4"> {noteId ? "Edit" : "New"} Note </Typography>
      <Divider sx={{ mb: 2, mt: 2 }} />
      <form onSubmit={handleSubmit}>
        <TextField
          label="Title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          fullWidth
          margin="normal"
          sx={{ mb: 2 }}
        />
        <ReactQuill
          ref={quillRef}
          value={formData.content}
          onChange={handleContentChange}
          placeholder="Content"
          modules={{
            toolbar: [
              ["bold", "italic", "underline", "strike"], // basic formatting
              [{ header: 1 }, { header: 2 }], // headers
              [{ list: "ordered" }, { list: "bullet" }], // lists
              [{ script: "sub" }, { script: "super" }],
              [{ size: ["small", "normal", "large", "huge"] }],
              [{ indent: "-1" }, { indent: "+1" }], // indentation
              [{ direction: "rtl" }], // text direction
              [{ align: [] }],
              [{ header: [1, 2, 3, 4, 5, 6, false] }], // custom header values
              [{ color: [] }, { background: [] }], // text and background color
              [{ font: [] }], // font family
              ["link", "image", "blockquote", "code-block"], // links, media, blockquote, code block
            ],
          }}
          formats={[
            "header",
            "font",
            "size",
            "bold",
            "italic",
            "direction",
            "align",
            "underline",
            "strike",
            "blockquote",
            "list",
            "bullet",
            "indent",
            "link",
            "image",
            "color",
            "background",
            "code-block",
            "script",
          ]}
          style={{
            height: "200px",
            width: "100%",
            marginBottom: 50,
          }}
        />
        <TextField
          type="date"
          label="Date"
          name="date"
          value={formData.date}
          InputLabelProps={{ shrink: true }}
          onChange={handleChange}
          fullWidth
          margin="normal"
          sx={{ mt: 2 }}
        />
        <FormControl fullWidth margin="normal">
          <InputLabel id="type-select-label">Type</InputLabel>
          <Select
            name="type"
            value={formData.type}
            onChange={handleChange}
            labelId="type-select-label"
            label="Type"
          >
            <MenuItem value="Goal">Goal</MenuItem>
            <MenuItem value="Meeting">Meeting</MenuItem>
            <MenuItem value="Personal">Personal</MenuItem>
          </Select>
        </FormControl>
        <Button type="submit" variant="contained" color="primary">
          Submit
        </Button>
      </form>
    </DashboardLayout>
  );
};

export default NotePage;
