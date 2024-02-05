import React, { useState, useEffect, useContext } from "react";
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
import { getAllUsers } from "../services/teamservice";
import Loading from "../components/Loading";
import { AlertContext } from "../contexts/AlertContext";
import { UserContext } from "../contexts/UserContext";
import SectionTitle from "../components/SectionTitle";
import CustomQuill from "../components/CustomQuill";

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
  const { setAlert } = useContext(AlertContext);
  const { user } = useContext(UserContext);

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
    const fetchNoteFeedbacks = async () => {
      try {
        const response = await getFeedbacks(noteId);
        setFeedbacks(response);
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
      }
    };
    const fetchNoteData = async () => {
      try {
        const response = await getNote(noteId);
        setFormData(response);
        setMentionedUsers(
          response.mentioned_users.map((item) => {
            return { name: "", email: item };
          }),
        );
        if (response.owner !== user.email) {
          setIsReadOnly(true);
        } else {
          fetchNoteFeedbacks();
        }
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
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
        setAllUsers(response);
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (validate(formData)) {
      try {
        formData.mentioned_users = mentionedUsers.map((item) => item.email);
        console.log(`sending form data: ${formData}`);
        if (noteId) {
          await updateNote(formData, noteId);
        } else {
          await createNote(formData);
        }
        localStorage.removeItem("noteFormData");
        navigate(`/notes?noteType=${formData.type}`);
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
      }
    }
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    try {
      await createFeedback(newFeedbackContent, noteId);
      navigate(`/dashboard`);
    } catch (error) {
      setAlert({
        message: "Something went wrong. Please try again later.",
        type: "error",
      });
    }
  };

  useEffect(() => {
    if (!noteId) {
      localStorage.setItem("noteFormData", JSON.stringify(formData));
    }
  }, [formData]);

  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }

  return (
    <>
      <SectionTitle title={`${noteId ? "ویرایش" : "ایجاد"} یادداشت`} />
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
        <CustomQuill
          isReadOnly={isReadOnly}
          value={formData.content}
          handleDataChange={(value) =>
            setFormData({ ...formData, content: value })
          }
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
          <SectionTitle title="نوشتن فیدبک" />
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
          <SectionTitle title="فیدبک‌ها" />
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
