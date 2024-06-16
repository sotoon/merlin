export const transformNoteResponse = (note: Note) => ({
  ...note,
  feedbackType:
    note.type === NOTE_TYPE.message
      ? note.title.startsWith(FEEDBACK_REQUEST_PREFIX)
        ? FEEDBACK_TYPE.Request
        : FEEDBACK_TYPE.Send
      : undefined,
  title: note.title.replace(new RegExp(`^${FEEDBACK_REQUEST_PREFIX}`), ''),
});
