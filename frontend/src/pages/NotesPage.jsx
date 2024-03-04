import React, { useEffect, useMemo, useState } from "react";
import { Link as RouterLink, useSearchParams } from "react-router-dom";

import AddSharpIcon from "@mui/icons-material/AddSharp";
import {
  Chip,
  Fab,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
} from "@mui/material";

import Loading from "../components/Loading";
import NoteCard from "../components/NoteCard";
import SectionTitle from "../components/SectionTitle";
import useFetchData from "../hooks/useFetchData";
import { getNotes } from "../services/noteservice";

const NoteTypeTitles = {
  Goal: "اهداف",
  Meeting: "جلسات",
  Personal: "شخصی",
  Task: "فعالیت‌ها",
  Proposal: "پروپوزال‌ها",
  Message: "پیام‌ها",
  Template: "قالب‌ها",
  "": "",
};

const NotesPage = () => {
  const [searchParams] = useSearchParams();
  const noteType = searchParams.get("noteType") || "";
  const userEmail = searchParams.get("useremail") || "";
  const userName = searchParams.get("username") || "";
  const retrieve_mentions = searchParams.get("retrieve_mentions") || false;
  const areNotesReadOnly = userEmail || retrieve_mentions;
  const [notes, setNotes] = useState([]);

  const [filters, setFilters] = useState({
    owner: "",
    type: noteType,
    showUnread: false,
  });

  const [sortCriteria, setSortCriteria] = useState({
    sortBy: "date",
    sortOrder: "asc",
  });
  const [owners, setOwners] = useState([]);

  const isLoading = useFetchData(
    () => getNotes(noteType, userEmail, retrieve_mentions),
    setNotes,
    [noteType, userEmail, retrieve_mentions],
  );

  let pageTitle = `یادداشت‌ها${noteType ? "ی" : ""} ${
    NoteTypeTitles[noteType]
  }`;
  if (userName) {
    pageTitle += `از کاربر ${userName}`;
  }
  if (retrieve_mentions) {
    pageTitle = "پیام‌ها";
  }
  useEffect(() => {
    const uniqueOwners = Array.from(new Set(notes.map((note) => note.owner)));
    setOwners(uniqueOwners);
  }, [notes]);
  const filteredAndSortedNotes = useMemo(() => {
    return notes
      .filter((note) => {
        return filters.owner ? note.owner === filters.owner : true;
      })
      .filter((note) => {
        return filters.type && !noteType ? note.type === filters.type : true;
      })
      .filter((note) => {
        return filters.showUnread ? note.read_status === false : true;
      })
      .sort((a, b) => {
        if (sortCriteria.sortOrder === "asc") {
          return new Date(a.date) - new Date(b.date);
        } else {
          return new Date(b.date) - new Date(a.date);
        }
      });
  }, [notes, filters, sortCriteria]);

  if (isLoading) {
    return <Loading description={"در حال دریافت اطلاعات"} />;
  }
  return (
    <>
      <SectionTitle title={pageTitle} />
      <Grid
        container
        spacing={2}
        style={{ marginBottom: "20px", marginTop: "20px" }}
      >
        <Grid item>
          {retrieve_mentions && (
            <FormControl
              margin="normal"
              sx={{ mt: 0, mr: 0, minWidth: "80px" }}
            >
              <InputLabel
                id="owner-select-label"
                style={{
                  textAlign: "right",
                  right: 0,
                  left: "auto",
                  marginRight: 15,
                }}
              >
                نویسنده
              </InputLabel>
              <Select
                name="owner"
                value={filters.owner}
                onChange={(e) =>
                  setFilters({ ...filters, owner: e.target.value })
                }
                labelId="owner-select-label"
                label="نویسنده"
              >
                <MenuItem value="">همه</MenuItem>
                {owners.map((owner, index) => (
                  <MenuItem key={index} value={owner}>
                    {owner}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
        </Grid>
        <Grid item>
          {!noteType && (
            <FormControl
              margin="normal"
              sx={{ mt: 0, mr: 0, minWidth: "50px" }}
            >
              <InputLabel
                id="type-select-label"
                style={{
                  textAlign: "right",
                  right: 0,
                  left: "auto",
                  marginRight: 25,
                }}
              >
                نوع
              </InputLabel>
              <Select
                name="type"
                value={filters.type}
                onChange={(e) =>
                  setFilters({ ...filters, type: e.target.value })
                }
                labelId="type-select-label"
                label="نوع"
              >
                <MenuItem value="">همه</MenuItem>
                {Object.entries(NoteTypeTitles).map(([key, value]) => (
                  <MenuItem key={key} value={key}>
                    {value}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
        </Grid>
        <Grid item>
          <FormControl margin="normal" sx={{ mt: 0, mr: 0, minWidth: "100px" }}>
            <InputLabel
              id="order-select-label"
              style={{
                textAlign: "right",
                right: 0,
                left: "auto",
                marginRight: 10,
              }}
            >
              ترتیب زمانی
            </InputLabel>
            <Select
              name="order"
              value={sortCriteria.sortOrder}
              onChange={(e) =>
                setSortCriteria({ ...sortCriteria, sortOrder: e.target.value })
              }
              labelId="order-select-label"
              label="ترتیب زمانی"
            >
              <MenuItem value="asc">صعودی</MenuItem>
              <MenuItem value="desc">نزولی</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item>
          <Chip
            label="خوانده نشده‌ها"
            onClick={() =>
              setFilters({ ...filters, showUnread: !filters.showUnread })
            }
            color={filters.showUnread ? "primary" : "default"}
            clickable
          />
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        {filteredAndSortedNotes.map((note, index) => (
          <Grid item xs={12} sm={12} md={12} key={index}>
            <NoteCard
              uuid={note.uuid}
              title={note.title}
              body={note.content}
              date={note.date}
              isReadOnly={areNotesReadOnly}
            />
          </Grid>
        ))}
      </Grid>
      <RouterLink to={noteType ? `/note?noteType=${noteType}` : "/note"}>
        <Fab
          color="secondary"
          aria-label="Add Note"
          sx={{
            position: "fixed",
            bottom: (theme) => theme.spacing(10),
            left: (theme) => theme.spacing(10),
            transform: "scale(1.2)",
          }}
        >
          <AddSharpIcon sx={{ transform: "scale(1.4)" }} />
        </Fab>
      </RouterLink>
    </>
  );
};

export default NotesPage;
