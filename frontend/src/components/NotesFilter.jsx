import React, { useEffect, useMemo, useState } from "react";

import {
  Chip,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
} from "@mui/material";
import PropTypes from "prop-types";

const NoteTypeOptions = {
  Goal: "اهداف",
  Meeting: "جلسات",
  Personal: "شخصی",
  Task: "فعالیت‌ها",
  Proposal: "پروپوزال‌ها",
  Message: "پیام‌ها",
};

const NotesFilter = ({
  notes,
  showWritersFilter,
  showTypeFilter,
  showUnreadFilter,
  handleFiltersChange,
}) => {
  const [filters, setFilters] = useState({
    owner: "",
    type: "",
    showUnread: false,
  });

  const [sortCriteria, setSortCriteria] = useState({
    sortBy: "date",
    sortOrder: "asc",
  });
  const [owners, setOwners] = useState([]);
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
        return filters.type ? note.type === filters.type : true;
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

  useEffect(() => {
    handleFiltersChange(filteredAndSortedNotes);
  }, [filteredAndSortedNotes]);

  return (
    <Grid
      container
      spacing={2}
      style={{ marginBottom: "20px", marginTop: "20px" }}
    >
      <Grid item>
        {showWritersFilter && (
          <FormControl margin="normal" sx={{ mt: 0, mr: 0, minWidth: "80px" }}>
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
        {showTypeFilter && (
          <FormControl margin="normal" sx={{ mt: 0, mr: 0, minWidth: "50px" }}>
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
              onChange={(e) => setFilters({ ...filters, type: e.target.value })}
              labelId="type-select-label"
              label="نوع"
            >
              <MenuItem value="">همه</MenuItem>
              {Object.entries(NoteTypeOptions).map(([key, value]) => (
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
        {showUnreadFilter && (
          <Chip
            label="خوانده نشده‌ها"
            onClick={() =>
              setFilters({ ...filters, showUnread: !filters.showUnread })
            }
            color={filters.showUnread ? "primary" : "default"}
            clickable
          />
        )}
      </Grid>
    </Grid>
  );
};

NotesFilter.propTypes = {
  notes: PropTypes.array,
  showWritersFilter: PropTypes.bool,
  showUnreadFilter: PropTypes.bool,
  showTypeFilter: PropTypes.bool,
  handleFiltersChange: PropTypes.func,
};

NotesFilter.defaultProps = {
  notes: [],
  showWritersFilter: false,
  showUnread: false,
  showTypeFilter: false,
  handleFiltersChange: () => {},
};

export default NotesFilter;
