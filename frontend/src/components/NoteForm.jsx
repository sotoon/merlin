import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Autocomplete,
  Button,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";

import CustomQuill from "../components/CustomQuill";
import { AlertContext } from "../contexts/AlertContext";
import { createNote, getTemplates, updateNote } from "../services/noteservice";
import { getAllUsers } from "../services/teamservice";
import SectionTitle from "./SectionTitle";

const NoteForm = ({ isReadOnly, noteData, noteId, defaultNoteType }) => {
  const [formData, setFormData] = useState(() => {
    const savedData = localStorage.getItem(`noteFormData${defaultNoteType}`);
    const emptyData = {
      title: "",
      content: "",
      date: "",
      type: defaultNoteType,
    };
    if (noteData) {
      return {
        title: noteData.title,
        content: noteData.content,
        date: noteData.date,
        type: noteData.type,
      };
    }
    return savedData ? JSON.parse(savedData) : emptyData;
  });
  const [mentionedUsers, setMentionedUsers] = useState(() =>
    noteData
      ? noteData.mentioned_users.map((item) => ({
          name: "",
          email: item,
        }))
      : [],
  );
  const [errors, setErrors] = useState({});
  const [allUsers, setAllUsers] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [template, setTemplate] = useState({ title: "", content: "" });
  const { setAlert } = useContext(AlertContext);
  const navigate = useNavigate();
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
    const fetchTemplates = async () => {
      try {
        const response = await getTemplates();
        setTemplates(response);
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
      }
    };
    fetchAllUsers();
    fetchTemplates();
  }, []);

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
        if (noteId) {
          await updateNote(formData, noteId);
        } else {
          await createNote(formData);
        }
        localStorage.removeItem(`noteFormData${formData.type}`);
        navigate(`/notes?noteType=${formData.type}`);
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
      }
    }
  };
  useEffect(() => {
    if (!noteId) {
      localStorage.setItem(
        `noteFormData${formData.type}`,
        JSON.stringify(formData),
      );
    }
  }, [formData]);
  useEffect(() => {
    setFormData({
      ...formData,
      title: formData.title + template.title,
      content: formData.content + template.content,
    });
  }, [template]);

  return (
    <>
      <SectionTitle title={`${noteId ? "ویرایش" : "ایجاد"} یادداشت`} />
      {!isReadOnly && (
        <FormControl
          margin="normal"
          errors={errors}
          helpertext={errors.template}
          sx={{ mr: 0, minWidth: "70px" }}
        >
          <InputLabel
            id="template-select-label"
            style={{
              textAlign: "right",
              right: 0,
              left: "auto",
              marginRight: 35,
            }}
          >
            قالب
          </InputLabel>
          <Select
            name="template"
            value={template}
            onChange={(event) => setTemplate(event.target.value)}
            labelId="template-select-label"
            label="Template"
            disabled={isReadOnly}
          >
            {templates.map((item) => (
              <MenuItem key={item.title} value={item}>
                {item.title}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
      {isReadOnly && (
        <Typography variant="h6">نویسنده: {noteData.owner_name} </Typography>
      )}
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
            setFormData((currentFormData) => ({
              ...currentFormData,
              content: value,
            }))
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
            <MenuItem value="Proposal">پروپوزال</MenuItem>
            <MenuItem value="Message">پیام</MenuItem>
            <MenuItem value="Template">قالب‌</MenuItem>
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
            ثبت
          </Button>
        )}
      </form>
    </>
  );
};

NoteForm.propTypes = {
  noteId: PropTypes.string,
  isReadOnly: PropTypes.bool,
  noteData: PropTypes.object,
  defaultNoteType: PropTypes.string,
};

NoteForm.defaultProps = {
  defaultNoteType: "Goal",
};

export default NoteForm;
