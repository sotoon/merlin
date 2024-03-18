import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Autocomplete,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
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
import {
  createNote,
  getNote,
  getNotes,
  getTemplates,
  updateNote,
} from "../services/noteservice";
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
  const [linkedNotes, setLinkedNotes] = useState([]);
  const [errors, setErrors] = useState({});
  const [allUsers, setAllUsers] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [allNotes, setAllNotes] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [pendingTemplate, setPendingTemplate] = useState({
    title: "",
    content: "",
  });
  const { setAlert } = useContext(AlertContext);
  const navigate = useNavigate();
  useEffect(() => {
    const fetchNoteData = async () => {
      try {
        setAllUsers(await getAllUsers());
        setTemplates(await getTemplates());
        setAllNotes(await getNotes());
        if (noteData) {
          let linked_notes = [];
          for (let i = 0; i < noteData.linked_notes.length; i++) {
            linked_notes.push(await getNote(noteData.linked_notes[i]));
          }
          setLinkedNotes(linked_notes);
        }
      } catch (error) {
        setAlert({
          message: "Something went wrong. Please try again later.",
          type: "error",
        });
      }
    };
    fetchNoteData();
  }, []);

  const validate = (data) => {
    let tempErrors = {};
    if (!data.title) tempErrors.title = "عنوان الزامی است.";
    if (!data.date) tempErrors.date = "تاریخ الزامی است.";
    if (!data.type) tempErrors.type = "نوع الزامی است.";
    setErrors(tempErrors);
    return Object.keys(tempErrors).length === 0;
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
        formData.linked_notes = linkedNotes.map((item) => item.uuid);
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
  const handleTemplateAction = (action) => {
    if (action === "append") {
      setFormData((prev) => ({
        ...prev,
        content: prev.content + pendingTemplate.content,
      }));
    } else if (action === "replace") {
      setFormData((prev) => ({
        ...prev,
        content: pendingTemplate.content,
      }));
    }
    setIsDialogOpen(false);
    setPendingTemplate({ title: "", content: "" });
  };

  return (
    <>
      <SectionTitle title={`${noteId ? "ویرایش" : "ایجاد"} یادداشت`} />
      {!isReadOnly && (
        <>
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
              value={pendingTemplate.title}
              onChange={(event) => {
                setPendingTemplate(event.target.value);
                setIsDialogOpen(true);
              }}
              labelId="template-select-label"
              label="Template"
              disabled={isReadOnly}
            >
              <MenuItem value=""></MenuItem>
              {templates.map((item) => (
                <MenuItem key={item.title} value={item}>
                  {item.title}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)}>
            <DialogTitle>{"استفاده از قالب"}</DialogTitle>
            <DialogContent>
              <DialogContentText>
                میخواهید قالب را اضافه یا جایگزین کنید؟
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => handleTemplateAction("append")}>
                اضافه
              </Button>
              <Button onClick={() => handleTemplateAction("replace")}>
                جایگزین
              </Button>
              <Button onClick={() => handleTemplateAction("cancel")}>
                بیخیال
              </Button>
            </DialogActions>
          </Dialog>
        </>
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
          onChange={(_, value) => {
            setMentionedUsers(value);
          }}
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
        <Autocomplete
          multiple
          id="linked-notes-autocomplete"
          options={allNotes}
          disabled={isReadOnly}
          getOptionLabel={(option) => option.title}
          isOptionEqualToValue={(option, value) => option.uuid == value.uuid}
          onChange={(_, value) => {
            setLinkedNotes(value || []);
          }}
          value={linkedNotes}
          renderInput={(params) => (
            <TextField
              {...params}
              label="یادداشت‌های لینک شده"
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
          renderOption={(props, option) => (
            <li {...props} key={option.uuid}>
              {option.title}{" "}
            </li>
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
