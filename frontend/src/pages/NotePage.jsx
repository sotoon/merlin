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
  FormHelperText,
} from "@mui/material";
import { createNote, getNote, updateNote } from "../services/noteservice";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import ReactQuill from "react-quill"; // Import the ReactQuill component
import "react-quill/dist/quill.snow.css";
import Loading from "../components/Loading";
import { ErrorContext } from "../contexts/ErrorContext";
import { UserContext } from "../contexts/UserContext";
const Quill = ReactQuill.Quill;
const Font = Quill.import("formats/font");
Font.whitelist = ["yekan", "sans-serif"]; // Add your fonts here
Quill.register(Font, true);

const NotePage = () => {
  const { noteId } = useParams();

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(noteId ? true : false);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [formData, setFormData] = useState(() => {
    const savedData = localStorage.getItem("noteFormData");
    return savedData
      ? JSON.parse(savedData)
      : { title: "", content: "", date: "", type: "" };
  });
  const navigate = useNavigate();
  const { setErrorMessage } = useContext(ErrorContext);
  const { user } = useContext(UserContext);
  let isProgrammaticUpdate = false;

  const quillRef = useRef(null);

  const validate = (data) => {
    let tempErrors = {};
    if (!data.title) tempErrors.title = "عنوان الزامی است.";
    if (!data.date) tempErrors.date = "تاریخ الزامی است.";
    if (!data.type) tempErrors.type = "نوع الزامی است.";
    // Add more validation rules as needed
    setErrors(tempErrors);
    return Object.keys(tempErrors).length === 0;
  };

  useEffect(() => {
    if (quillRef.current) {
      const quill = quillRef.current.getEditor();
      isProgrammaticUpdate = true;
      quill.setText(" ");

      quill.format("size", "large");
      quill.format("direction", "rtl");
      quill.format("align", "right");
      quill.format("font", "yekan");

      quill.deleteText(0, 1);
      isProgrammaticUpdate = false;
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
        if (response.data.owner !== user.username) {
          setIsReadOnly(true);
        }
      } catch (error) {
        console.error(error);
        setErrorMessage("Something went wrong. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };
    if (noteId) {
      fetchNoteData();
    }
  }, [noteId, user]);

  const handleChange = (e) => {
    setErrors({ ...errors, [e.target.name]: "" });
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleContentChange = (value, delta, source, editor) => {
    setFormData({
      ...formData,
      content: value,
    });
    if (isProgrammaticUpdate) {
      return;
    }
    if (editor.getLength() <= 1 && quillRef.current) {
      const quill = quillRef.current.getEditor();
      isProgrammaticUpdate = true;
      quill.setText(" ");

      quill.format("size", "large");
      quill.format("direction", "rtl");
      quill.format("align", "right");
      quill.format("font", "yekan");

      quill.deleteText(0, 1);
      isProgrammaticUpdate = false;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (validate(formData)) {
      try {
        if (noteId) {
          const response = await updateNote(formData, noteId);
          console.log(
            `response status: ${
              response.status
            } response data: ${JSON.stringify(response.data)}`,
          );
        } else {
          const response = await createNote(formData);
          console.log(
            `response status: ${
              response.status
            } response data: ${JSON.stringify(response.data)}`,
          );
        }
        navigate("/dashboard");
      } catch (error) {
        console.error(error);
        setErrorMessage("Something went wrong. Please try again later.");
      }
    }
  };

  useEffect(() => {
    if (!noteId) {
      localStorage.setItem("noteFormData", JSON.stringify(formData));
    }
  }, [formData]);

  if (isLoading) {
    return (
      <DashboardLayout>
        <Loading description={"در حال دریافت اطلاعات"} />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Typography variant="h4">
        {" "}
        {noteId ? "ویرایش" : "ایجاد"} یادداشت
      </Typography>
      <Divider sx={{ mb: 2, mt: 2 }} />
      <form onSubmit={handleSubmit}>
        <TextField
          label="عنوان"
          name="title"
          value={formData.title}
          onChange={handleChange}
          error={Boolean(errors.title)}
          helpertext={errors.title}
          fullWidth
          margin="normal"
          sx={{ mb: 2 }}
          InputProps={{
            readOnly: isReadOnly,
            style: {
              textAlign: "right", // Align input text to the right
              direction: "rtl", // Set input text direction to right-to-left
            },
          }}
          InputLabelProps={{
            style: {
              textAlign: "right", // Align label text to the right
              right: 0, // Position label to the right
              left: "auto", // Override default left positioning
              marginRight: 20,
            },
          }}
        />
        <ReactQuill
          ref={quillRef}
          value={formData.content}
          onChange={handleContentChange}
          placeholder="محتوا"
          readOnly={isReadOnly}
          modules={{
            toolbar: [
              ["bold", "italic", "underline", "strike"], // basic formatting
              [{ header: 1 }, { header: 2 }], // headers
              [{ list: "ordered" }, { list: "bullet" }], // lists
              [{ script: "sub" }, { script: "super" }],
              [{ size: ["small", false, "large", "huge"] }],
              [{ indent: "-1" }, { indent: "+1" }], // indentation
              [{ direction: "rtl" }], // text direction
              [{ align: [] }],
              [{ header: [1, 2, 3, 4, 5, 6, false] }], // custom header values
              [{ color: [] }, { background: [] }], // text and background color
              [{ font: Font.whitelist }], // font family
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
            width: "100%",
            marginBottom: 10,
            direction: "ltr",
          }}
        />
        <TextField
          type="date"
          label="تاریخ"
          name="date"
          error={Boolean(errors.date)}
          helpertext={errors.date}
          value={formData.date}
          InputProps={{
            readOnly: isReadOnly,
          }}
          InputLabelProps={{
            shrink: true,
            style: {
              textAlign: "right", // Align label text to the right
              right: 0, // Position label to the right
              left: "auto", // Override default left positioning
              marginRight: 20,
            },
          }}
          onChange={handleChange}
          margin="normal"
          sx={{ mt: 2 }}
        />
        <FormControl
          margin="normal"
          errors={errors}
          helpertext={errors.type}
          sx={{ mr: 5, minWidth: "50px" }}
        >
          <InputLabel
            id="type-select-label"
            style={{
              textAlign: "right", // Align label text to the right
              right: 0, // Position label to the right
              left: "auto", // Override default left positioning
              marginRight: 35,
            }}
          >
            نوع
          </InputLabel>
          <Select
            name="type"
            value={formData.type}
            onChange={handleChange}
            labelId="type-select-label"
            label="Type"
            disabled={isReadOnly}
          >
            <MenuItem value="Goal">هدف</MenuItem>
            <MenuItem value="Meeting">جلسه</MenuItem>
            <MenuItem value="Personal">شخصی</MenuItem>
          </Select>
          {errors.type && (
            <FormHelperText sx={{ color: (theme) => theme.palette.error.main }}>
              {errors.type}
            </FormHelperText>
          )}
        </FormControl>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          sx={{ display: "flex" }}
        >
          Submit
        </Button>
      </form>
    </DashboardLayout>
  );
};

export default NotePage;
