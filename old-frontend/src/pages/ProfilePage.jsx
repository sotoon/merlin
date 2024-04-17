import React, { useContext, useState } from "react";

import { Button, Chip, TextField, Typography } from "@mui/material";

import Loading from "../components/Loading";
import SectionTitle from "../components/SectionTitle";
import { AlertContext } from "../contexts/AlertContext";
import { UserContext } from "../contexts/UserContext";
import useFetchData from "../hooks/useFetchData";
import { getProfileData, updateProfile } from "../services/authservice";
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
  const { setAlert } = useContext(AlertContext);
  const isLoading = useFetchData(getProfileData, setFormData, []);
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
        await updateProfile(formData);
        setAlert({
          message: "تغییرات با موفقیت ثبت شد",
          type: "success",
        });
        const token = localStorage.getItem("accessToken");
        const user = await verifyToken(token);
        setUser(user);
      } catch (error) {
        setAlert({
          message: "ویرایش پروفایل ناموفق بود، دوباره تلاش کنید.",
          type: "error",
        });
      }
    };
    updateProfileData();
  };

  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }
  return (
    <>
      <SectionTitle title={"ویرایش پروفایل"} />
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
      <Chip
        label={`سطح: ${formData.level}`}
        color="warning"
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
    </>
  );
};

export default ProfilePage;
