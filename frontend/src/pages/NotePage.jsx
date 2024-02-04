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
  Autocomplete,
  Card,
  CardHeader,
  CardContent,
  Grid,
} from "@mui/material";
import {
  createNote,
  getNote,
  updateNote,
  createFeedback,
  getFeedbacks,
} from "../services/noteservice";
import { useParams, useNavigate } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import { getAllUsers } from "../services/teamservice";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import Loading from "../components/Loading";
import { ErrorContext } from "../contexts/ErrorContext";
import { UserContext } from "../contexts/UserContext";
const Quill = ReactQuill.Quill;
const Font = Quill.import("formats/font");
Font.whitelist = ["yekan", "sans-serif"];
Quill.register(Font, true);

const NotePage = () => {
  const { noteId } = useParams();

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(noteId ? true : false);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [mentionedUsers, setMentionedUsers] = useState([]);
  const [newFeedbackContent, setNewFeedbackContent] = useState("");
  const [feedbacks, setFeedbacks] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [formData, setFormData] = useState(() => {
    const savedData = localStorage.getItem("noteFormData");
    const emptyData = { title: "", content: "", date: "", type: "" };
    if (noteId) {
      return emptyData;
    }
    return savedData ? JSON.parse(savedData) : emptyData;
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
    setErrors(tempErrors);
    return Object.keys(tempErrors).length === 0;
  };

  const handleMentionChange = (_, value) => {
    setMentionedUsers(value);
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
    const fetchNoteFeedbacks = async () => {
      try {
        const response = await getFeedbacks(noteId);
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setFeedbacks(response.data);
      } catch (error) {
        console.error(error);
        setErrorMessage("Something went wrong. Please try again later.");
      }
    };
    const fetchNoteData = async () => {
      try {
        const response = await getNote(noteId);
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setFormData(response.data);
        setMentionedUsers(
          response.data.mentioned_users.map((item) => {
            return { name: "", email: item };
          }),
        );
        if (response.data.owner !== user.email) {
          setIsReadOnly(true);
        } else {
          fetchNoteFeedbacks();
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

  useEffect(() => {
    const fetchAllUsers = async () => {
      try {
        const response = await getAllUsers();
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setAllUsers(response.data);
      } catch (error) {
        console.error(error);
        setErrorMessage("Something went wrong. Please try again later.");
      }
    };

    fetchAllUsers();
  }, []);

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
        formData.mentioned_users = mentionedUsers.map((item) => item.email);
        console.log(`sending form data: ${formData}`);
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
        localStorage.removeItem("noteFormData");
        navigate(`/notes?noteType=${formData.type}`);
      } catch (error) {
        console.error(error);
        setErrorMessage("Something went wrong. Please try again later.");
      }
    }
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await createFeedback(newFeedbackContent, noteId);
      console.log(
        `response status: ${response.status} response data: ${JSON.stringify(
          response.data,
        )}`,
      );
      navigate(`/dashboard`);
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

  if (isLoading) {
    return (
      <DashboardLayout>
        <Loading description={"در حال دریافت اطلاعات"} />
      </DashboardLayout>
    );
  }

  return (
    <>
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
              textAlign: "right",
              direction: "rtl",
            },
          }}
          InputLabelProps={{
            style: {
              textAlign: "right",
              right: 0,
              left: "auto",
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
              ["bold", "italic", "underline", "strike"],
              [{ header: 1 }, { header: 2 }],
              [{ list: "ordered" }, { list: "bullet" }],
              [{ script: "sub" }, { script: "super" }],
              [{ size: ["small", false, "large", "huge"] }],
              [{ indent: "-1" }, { indent: "+1" }],
              [{ direction: "rtl" }],
              [{ align: [] }],
              [{ header: [1, 2, 3, 4, 5, 6, false] }],
              [{ color: [] }, { background: [] }],
              [{ font: Font.whitelist }],
              ["link", "image", "blockquote", "code-block"],
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
              textAlign: "right",
              right: 0,
              left: "auto",
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
              textAlign: "right",
              right: 0,
              left: "auto",
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
            <MenuItem value="Task">فعالیت</MenuItem>
          </Select>
          {errors.type && (
            <FormHelperText sx={{ color: (theme) => theme.palette.error.main }}>
              {errors.type}
            </FormHelperText>
          )}
        </FormControl>

        <Autocomplete
          multiple
          id="user-autocomplete"
          options={allUsers}
          disabled={isReadOnly}
          getOptionLabel={(option) => `${option.name}(${option.email})`}
          isOptionEqualToValue={(option, value) => option.email == value.email}
          onChange={handleMentionChange}
          value={mentionedUsers}
          renderInput={(params) => (
            <TextField
              {...params}
              label="منشن‌ شوندگان"
              variant="outlined"
              sx={{ mt: 2, mb: 2 }}
              InputLabelProps={{
                style: {
                  textAlign: "right",
                  right: 0,
                  left: "auto",
                  marginRight: 20,
                },
              }}
            />
          )}
        />

        {!isReadOnly && (
          <Button
            type="submit"
            variant="contained"
            color="primary"
            sx={{ display: "flex" }}
          >
            Submit
          </Button>
        )}
      </form>
      {isReadOnly && (
        <>
          <Typography variant="h4">نوشتن فیدبک</Typography>
          <Divider sx={{ mb: 2, mt: 2 }} />
          <form onSubmit={handleFeedbackSubmit}>
            <TextField
              label="فیدبک"
              name="feedback"
              value={newFeedbackContent}
              placeholder="نوشتن فیدبک"
              onChange={(e) => setNewFeedbackContent(e.target.value)}
              multiline
              fullWidth
              rows={4}
              margin="normal"
              sx={{
                mb: 2,
              }}
              InputProps={{
                style: {
                  textAlign: "right",
                  direction: "rtl",
                },
              }}
              InputLabelProps={{
                style: {
                  textAlign: "right",
                  right: 0,
                  left: "auto",
                  marginRight: 20,
                },
              }}
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              sx={{ display: "flex" }}
            >
              Submit
            </Button>
          </form>
        </>
      )}
      {!isReadOnly && (
        <>
          <Typography variant="h4" sx={{ mt: 5 }}>
            فیدبک‌ها
          </Typography>
          <Divider sx={{ mb: 2, mt: 2 }} />

          <Grid container spacing={2}>
            {feedbacks.map((feedback, index) => (
              <Grid item xs={12} sm={12} md={12} key={index}>
                <Card
                  sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  <CardHeader
                    title={
                      <Typography variant="h6">
                        {feedback.owner_name}
                      </Typography>
                    }
                    sx={{ backgroundColor: "#0D47A1", color: "#FFFFFF" }}
                  />
                  <Divider />
                  <CardContent sx={{ flex: "1 0 auto" }}>
                    <Typography
                      variant="body"
                      color="textSecondary"
                      component="div"
                    >
                      {feedback.content}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}
    </>
  );
};

export default NotePage;
