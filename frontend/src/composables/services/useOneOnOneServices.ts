import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import dayjs from '~/utils/dayjs';

interface Error {
  detail?: string;
}

export const useGetOneOnOneList = ({
  userId,
  search,
  sort,
  dateRange,
}: {
  userId: string;
  search?: Ref<string | undefined>;
  sort?: Ref<keyof typeof ONE_ON_ONE_SORT_OPTION | undefined>;
  dateRange?: Ref<{ from: Date; to: Date } | undefined>;
}) => {
  const { $api } = useNuxtApp();
  return useQuery<Schema<'OneOnOne'>[]>({
    queryKey: computed(() => [
      'one-on-one-list',
      userId,
      search?.value,
      sort?.value,
      dateRange?.value?.from
        ? dayjs(dateRange.value.from)
            .startOf('day')
            .format('YYYY-MM-DDTHH:mm:ss')
        : undefined,
      dateRange?.value?.to
        ? dayjs(dateRange.value.to).endOf('day').format('YYYY-MM-DDTHH:mm:ss')
        : undefined,
    ]),
    queryFn: () => {
      const params: Record<string, string | undefined> = {
        search: search?.value || undefined,
        sort: sort?.value,
      };

      if (dateRange?.value?.from && dateRange.value.to) {
        // Send formatted datetime strings with start and end of day times
        params.date_from = dayjs(dateRange.value.from)
          .startOf('day')
          .format('YYYY-MM-DDTHH:mm:ss');
        params.date_to = dayjs(dateRange.value.to)
          .endOf('day')
          .format('YYYY-MM-DDTHH:mm:ss');
      }

      return $api.fetch(`/my-team/${userId}/one-on-ones/`, {
        params,
      });
    },
    enabled: !!userId,
  });
};

export const useCreateOneOnOne = ({ userId }: { userId: string }) => {
  const { $api } = useNuxtApp();
  const queryClient = useQueryClient();

  return useMutation<Schema<'OneOnOne'>, Error, Schema<'OneOnOneRequest'>>({
    mutationFn: (data) =>
      $api.fetch(`/my-team/${userId}/one-on-ones/`, {
        method: 'POST',
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        predicate: (query) => {
          return (
            query.queryKey[0] === 'one-on-one-list' &&
            query.queryKey[1] === userId
          );
        },
      });
    },
  });
};

export const useUpdateOneOnOne = ({
  userId,
  oneOnOneId,
}: {
  userId: string;
  oneOnOneId: number;
}) => {
  const { $api } = useNuxtApp();
  const queryClient = useQueryClient();

  return useMutation<
    Schema<'OneOnOne'>,
    Error,
    Schema<'PatchedOneOnOneRequest'>
  >({
    mutationFn: (data) =>
      $api.fetch(`/my-team/${userId}/one-on-ones/${oneOnOneId}/`, {
        method: 'PATCH',
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        predicate: (query) => {
          return (
            query.queryKey[0] === 'one-on-one-list' &&
            query.queryKey[1] === userId
          );
        },
      });
      queryClient.invalidateQueries({
        queryKey: ['one-on-one', String(oneOnOneId)],
      });
    },
  });
};

export const useGetOneOnOne = ({
  userId,
  oneOnOneId,
}: {
  userId: string;
  oneOnOneId: string;
}) => {
  const { $api } = useNuxtApp();

  return useQuery<Schema<'OneOnOne'>>({
    queryKey: ['one-on-one', oneOnOneId],
    queryFn: () => $api.fetch(`/my-team/${userId}/one-on-ones/${oneOnOneId}/`),
    enabled: !!userId && !!oneOnOneId,
  });
};

export const useGetOneOnOneTags = () => {
  const { $api } = useNuxtApp();

  return useQuery<Schema<'TagRead'>[]>({
    queryKey: ['one-on-one-tags'],
    queryFn: () => $api.fetch('/value-tags/'),
  });
};
