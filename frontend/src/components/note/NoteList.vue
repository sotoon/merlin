<template>
  <ul class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3">
    <li v-for="note in notes" :key="note.uuid">
      <NuxtLink :to="getNoteRoute(note)">
        <NoteCard
          :note="note"
          :display-writer="displayWriter"
          :display-type="displayType"
          :display-read-status="displayReadStatus"
        />
      </NuxtLink>
    </li>
  </ul>
</template>

<script lang="ts" setup>
const props = defineProps<{
  notes: Note[];
  displayWriter?: boolean;
  displayType?: boolean;
  displayReadStatus?: boolean;
}>();

function getNoteRoute(note: Note) {
  const getRouteNameAndParams: () => {
    name: string;
    params: Record<string, any>;
    query?: Record<string, any>;
  } = () => {
    switch (note.type) {
      case NOTE_TYPE.template:
        return {
          name: 'template',
          params: { id: note.uuid },
        };
      case NOTE_TYPE.oneOnOne:
        return {
          name: 'one-on-one-id',
          params: {
            userId: note.one_on_one_member,
            id: note.one_on_one_id,
          },
        };
      case NOTE_TYPE.feedbackRequest:
        return {
          name: 'feedback-detail',
          params: { requestId: note.feedback_request_uuid },
        };
      case NOTE_TYPE.feedback:
        return {
          name: 'adhoc-feedback-detail',
          params: { id: note.feedback_uuid },
        };
      default:
        return {
          name: 'note',
          params: {
            type: NOTE_TYPE_ROUTE_PARAM[note.type],
            id: note.uuid,
          },
        };
    }
  };

  const routeObj = getRouteNameAndParams();

  if (props.displayReadStatus && !note.read_status) {
    routeObj.query = { read: 'true' };
  }

  return routeObj;
}
</script>
