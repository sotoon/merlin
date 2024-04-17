import React, { useContext, useState } from "react";

import {
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
} from "@mui/material";
import { PropTypes } from "prop-types";

import { AlertContext } from "../contexts/AlertContext";
import useFetchData from "../hooks/useFetchData";
import { createNoteSummary, getNoteSummary } from "../services/noteservice";
import Loading from "./Loading";
import SectionTitle from "./SectionTitle";

const VALID_NOTE_TYPES = ["Proposal", "Goal"];

const SummaryForm = ({ noteId, isReadOnly, noteType }) => {
  const [summaryData, setSummaryData] = useState({
    content: "",
    performance_label: "",
    ladder_change: "",
    bonus: 0,
    salary_change: 0,
    committee_date: "",
  });
  const isLoading = useFetchData(
    () => (noteId ? getNoteSummary(noteId) : null),
    (response) =>
      setSummaryData(response.length > 0 ? response[0] : { content: "" }),
    [noteId],
  );
  const { setAlert } = useContext(AlertContext);
  const handleSummarySubmit = async (e) => {
    e.preventDefault();
    try {
      await createNoteSummary(summaryData, noteId);
      setAlert({
        message: "جمع‌بندی با موفقیت افزوده شد!",
        type: "success",
      });
    } catch (error) {
      setAlert({
        message: "Something went wrong. Please try again later.",
        type: "error",
      });
    }
  };
  if (!VALID_NOTE_TYPES.includes(noteType)) {
    return <></>;
  }
  if (isLoading) {
    return <Loading description="در حال دریافت اطلاعات..." />;
  }
  return (
    <>
      <SectionTitle title="جمع‌بندی" />
      <form onSubmit={handleSummarySubmit}>
        <TextField
          label="جمع‌بندی"
          name="summary"
          value={summaryData.content}
          placeholder="جمع‌بندی"
          onChange={(e) =>
            setSummaryData({ ...summaryData, content: e.target.value })
          }
          multiline
          fullWidth
          rows={4}
          margin="normal"
          sx={{
            mb: 2,
          }}
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
        <FormControl margin="normal" sx={{ minWidth: "120px" }}>
          <InputLabel
            id="performance-select-label"
            style={{
              textAlign: "right",
              right: 0,
              left: "auto",
              marginRight: 20,
            }}
          >
            لیبل عملکردی
          </InputLabel>
          <Select
            name="performanceLabel"
            value={summaryData.performance_label}
            onChange={(e) =>
              setSummaryData({
                ...summaryData,
                performance_label: e.target.value,
              })
            }
            labelId="performance-select-label"
            label="PerformanceLabel"
            disabled={isReadOnly}
          >
            <MenuItem value="نیاز به بهبود">نیاز به بهبود</MenuItem>
            <MenuItem value="در حد انتظار">در حد انتظار</MenuItem>
            <MenuItem value="فراتر از حد انتظار">فراتر از حد انتظار</MenuItem>
            <MenuItem value="به طور ویژه‌ای فراتر از حد انتظار">
              به طور ویژه‌ای فراتر از حد انتظار
            </MenuItem>
          </Select>
        </FormControl>
        <TextField
          label="تغییر در سطح لدر"
          name="ladderChange"
          value={summaryData.ladder_change}
          onChange={(e) =>
            setSummaryData({ ...summaryData, ladder_change: e.target.value })
          }
          margin="normal"
          sx={{ mb: 2, mr: 5 }}
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
              marginRight: 15,
            },
          }}
        />
        <FormControl margin="normal" sx={{ mr: 5, minWidth: "120px" }}>
          <InputLabel
            id="bonus-select-label"
            style={{
              textAlign: "right",
              right: 0,
              left: "auto",
              marginRight: 10,
            }}
          >
            پاداش عملکردی
          </InputLabel>
          <Select
            name="bonus"
            value={summaryData.bonus}
            onChange={(e) =>
              setSummaryData({
                ...summaryData,
                bonus: e.target.value,
              })
            }
            labelId="bonus-select-label"
            label="bonus"
            disabled={isReadOnly}
          >
            <MenuItem value="0">0%</MenuItem>
            <MenuItem value="5">5%</MenuItem>
            <MenuItem value="10">10%</MenuItem>
            <MenuItem value="15">15%</MenuItem>
            <MenuItem value="20">20%</MenuItem>
          </Select>
        </FormControl>
        <FormControl margin="normal" sx={{ mr: 5, minWidth: "150px" }}>
          <InputLabel
            id="salary-select-label"
            style={{
              textAlign: "right",
              right: 0,
              left: "auto",
              marginRight: 10,
            }}
          >
            تغییر پله‌ی حقوقی
          </InputLabel>
          <Select
            name="salaryChange"
            value={summaryData.salary_change}
            onChange={(e) =>
              setSummaryData({
                ...summaryData,
                salary_change: e.target.value,
              })
            }
            labelId="salary-select-label"
            label="salaryChange"
            disabled={isReadOnly}
          >
            <MenuItem value="0">0</MenuItem>
            <MenuItem value="0.5">0.5</MenuItem>
            <MenuItem value="1">1</MenuItem>
            <MenuItem value="1.5">1.5</MenuItem>
            <MenuItem value="2">2</MenuItem>
            <MenuItem value="2.5">2.5</MenuItem>
            <MenuItem value="3">3</MenuItem>
          </Select>
        </FormControl>
        <TextField
          type="date"
          label="تاریخ کمیته"
          name="committeeDate"
          value={summaryData.committee_date}
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
          onChange={(e) =>
            setSummaryData({ ...summaryData, committee_date: e.target.value })
          }
          margin="normal"
          sx={{ mt: 2, mr: 5 }}
        />
        {!isReadOnly && (
          <Button
            type="submit"
            variant="contained"
            color="primary"
            sx={{ display: "flex" }}
          >
            نوشتن جمع‌بندی
          </Button>
        )}
      </form>
    </>
  );
};

SummaryForm.propTypes = {
  noteId: PropTypes.string,
  summary: PropTypes.string,
  isReadOnly: PropTypes.bool,
  noteType: PropTypes.string,
};

SummaryForm.defaultProps = {
  noteId: "",
  summary: "",
  isReadOnly: true,
  noteType: "",
};

export default SummaryForm;
