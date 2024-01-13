import React, { useState, useEffect } from "react";
import {
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";
import ReactQuill from "react-quill"; // Import the ReactQuill component
import "react-quill/dist/quill.snow.css";

const NewNote = () => {
  const [formData, setFormData] = useState(() => {
    const savedData = localStorage.getItem("noteFormData");
    return savedData
      ? JSON.parse(savedData)
      : { title: "", content: "", date: "", type: "" };
  });
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

  const handleSubmit = (e) => {
    e.preventDefault();

    // TODO: Add code to send formData to your backend API
    console.log(formData);
  };

  useEffect(() => {
    localStorage.setItem("noteFormData", JSON.stringify(formData));
  }, [formData]);

  return (
    <DashboardLayout>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          fullWidth
          margin="normal"
        />
        <ReactQuill
          value={formData.content}
          onChange={handleContentChange}
          placeholder="Content"
          modules={{
            toolbar: [
              [{ header: [1, 2, false] }],
              ["bold", "italic", "underline", "strike", "blockquote"],
              [{ list: "ordered" }, { list: "bullet" }],
              ["link", "image"],
              ["clean"],
            ],
          }}
          formats={[
            "header",
            "bold",
            "italic",
            "underline",
            "strike",
            "blockquote",
            "list",
            "bullet",
            "link",
            "image",
          ]}
          style={{ width: "100%", marginBottom: "16px" }}
        />
        <TextField
          type="date"
          label="Date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          fullWidth
          margin="normal"
        />
        <FormControl fullWidth margin="normal">
          <InputLabel>Type</InputLabel>
          <Select name="type" value={formData.type} onChange={handleChange}>
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

export default NewNote;
