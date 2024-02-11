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
} from "@mui/material";
import PropTypes from "prop-types";

import CustomQuill from "../components/CustomQuill";
import { AlertContext } from "../contexts/AlertContext";
import { createNote, updateNote } from "../services/noteservice";
import { getAllUsers, getCommittees } from "../services/teamservice";
import SectionTitle from "./SectionTitle";

const NoteForm = ({ isReadOnly, noteData, noteId, defaultNoteType }) => {
  const [formData, setFormData] = useState(() => {
    const savedData = localStorage.getItem(`noteFormData${defaultNoteType}`);
    const emptyData = {
      title: "",
      content: "",
      date: "",
      type: defaultNoteType,
      committee: "",
    };
    if (noteData) {
      return {
        title: noteData.title,
        content: noteData.content,
        date: noteData.date,
        type: noteData.type,
        committee: noteData.committee,
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
  const [committees, setCommittees] = useState([]);
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
    const fetchCommittees = async () => {
      try {
        const response = await getCommittees();
        setCommittees(response.map((item) => item.name));
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
      }
    };
    fetchAllUsers();
    fetchCommittees();
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
            <MenuItem value="Proposal">پروپوزال</MenuItem>
          </Select>
          {errors.type && (
            <FormHelperText sx={{ color: (theme) => theme.palette.error.main }}>
              {errors.type}
            </FormHelperText>
          )}
        </FormControl>
        {formData.type === "Proposal" && (
          <FormControl
            margin="normal"
            errors={errors}
            helpertext={errors.committee}
            sx={{ mr: 5, minWidth: "70px" }}
          >
            <InputLabel
              id="committee-select-label"
              style={{
                textAlign: "right",
                right: 0,
                left: "auto",
                marginRight: 35,
              }}
            >
              کمیته
            </InputLabel>
            <Select
              name="committee"
              value={formData.committee}
              onChange={handleChange}
              labelId="committee-select-label"
              label="Committeee"
              disabled={isReadOnly}
            >
              {committees.map((item) => (
                <MenuItem key={item} value={item}>
                  {item}
                </MenuItem>
              ))}
            </Select>
            {errors.committeee && (
              <FormHelperText
                sx={{ color: (theme) => theme.palette.error.main }}
              >
                {errors.committee}
              </FormHelperText>
            )}
          </FormControl>
        )}

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
