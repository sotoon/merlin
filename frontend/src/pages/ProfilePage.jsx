import React, { useState, useEffect, useContext } from "react";
import DashboardLayout from "../components/DashboardLayout";
import { getProfileData, updateProfile } from "../services/authservice";
import {
  TextField,
  Button,
  Typography,
  Divider,
  Snackbar,
  Alert,
  Chip,
} from "@mui/material";
import Loading from "../components/Loading";
import { ErrorContext } from "../contexts/ErrorContext";
import { UserContext } from "../contexts/UserContext";
import { verifyToken } from "../services/authservice";

const ProfilePage = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    gmail: "",
    phone: "",
    department: "",
    chapter: "",
    team: "",
    leader: "",
  });
  const { setUser } = useContext(UserContext);
  const [isLoading, setIsLoading] = useState(true);
  const { setErrorMessage } = useContext(ErrorContext);
  const [isSubmitSnackbarOpen, setIsSubmitSnackbarOpen] = useState(false);
  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const response = await getProfileData();
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setFormData(response.data);
      } catch (error) {
        console.error(error);
        setErrorMessage("Something went wrong. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfileData();
  }, []);
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const updateProfileData = async () => {
      try {
        const response = await updateProfile(formData);
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setIsSubmitSnackbarOpen(true);
        const token = localStorage.getItem("accessToken");
        const user = await verifyToken(token);
        setUser(user);
      } catch (error) {
        console.error(error);
        setErrorMessage("Something went wrong. Please try again later.");
      }
    };
    updateProfileData();
  };

  const handleSubmitSnackbarClose = () => {
    setIsSubmitSnackbarOpen(false);
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <Loading description={"در حال دریافت اطلاعات"} />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Typography variant="h4">ویرایش پروفایل</Typography>
      <Divider sx={{ mb: 2, mt: 2 }} />
      <Typography variant="h6" gutterBottom>
        ایمیل سازمانی: {formData.email}
      </Typography>
      <Chip
        label={`دپارتمان: ${formData.department}`}
        color="primary"
        sx={{ fontSize: "large" }}
      />
      <Chip
        label={`چپتر: ${formData.chapter}`}
        color="secondary"
        sx={{ margin: 1, fontSize: "large" }}
      />
      <Chip
        label={`تیم: ${formData.team}`}
        color="success"
        sx={{ margin: 1, fontSize: "large" }}
      />
      <Chip
        label={`لیدر: ${formData.leader}`}
        color="error"
        sx={{ margin: 1, fontSize: "large" }}
      />
      <form onSubmit={handleSubmit}>
        <TextField
          label="نام"
          name="name"
          value={formData.name}
          onChange={handleChange}
          fullWidth
          margin="normal"
          sx={{ mb: 2 }}
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
        <TextField
          label="جیمیل"
          name="gmail"
          value={formData.gmail}
          onChange={handleChange}
          fullWidth
          margin="normal"
          sx={{ mb: 2 }}
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
        <TextField
          label="موبایل"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          fullWidth
          margin="normal"
          sx={{ mb: 2 }}
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
          ثبت تغییرات
        </Button>
      </form>
      <Snackbar
        open={isSubmitSnackbarOpen}
        autoHideDuration={6000}
        onClose={handleSubmitSnackbarClose}
      >
        <Alert
          onClose={handleSubmitSnackbarClose}
          severity="success"
          sx={{ width: "100%" }}
        >
          تغییرات با موفقیت ثبت شد
        </Alert>
      </Snackbar>
    </DashboardLayout>
  );
};

export default ProfilePage;
