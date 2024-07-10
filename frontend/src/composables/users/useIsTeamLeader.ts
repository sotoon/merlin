export const useIsTeamLeader = () => {
  const { data: users } = useGetMyTeam();
  const isTeamLeader = computed(() => Boolean(users.value?.length));

  return isTeamLeader;
};
