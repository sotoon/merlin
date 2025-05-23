interface Error {
  detail?: string;
}

export const useGetOneOnOneList = ({ userId }: { userId: string }) =>
  useApiFetch<Schema<'OneOnOne'>[]>(`/my-team/${userId}/one-on-ones/`, {
    key: createNuxtDataKey(['one-on-one-list', userId]),
  });

export const useCreateOneOnOne = ({ userId }: { userId: string }) =>
  useApiMutation<Schema<'OneOnOne'>, Error, Schema<'OneOnOneRequest'>>(
    `/my-team/${userId}/one-on-ones/`,
    {
      method: 'POST',
      onSuccess: () => {
        invalidateNuxtData(['one-on-one-list', userId]);
      },
    },
  );

export const useUpdateOneOnOne = ({
  userId,
  oneOnOneId,
}: {
  userId: string;
  oneOnOneId: number;
}) =>
  useApiMutation<Schema<'OneOnOne'>, Error, Schema<'PatchedOneOnOneRequest'>>(
    `/my-team/${userId}/one-on-ones/${oneOnOneId}/`,
    {
      method: 'PATCH',
      onSuccess: (oneOnOne) => {
        invalidateNuxtData(['one-on-one-list', userId]);
        invalidateNuxtData(['one-on-one', oneOnOne.id]);
      },
    },
  );

export const useGetOneOnOne = ({
  userId,
  oneOnOneId,
}: {
  userId: string;
  oneOnOneId: string;
}) =>
  useApiFetch<Schema<'OneOnOne'>>(
    `/my-team/${userId}/one-on-ones/${oneOnOneId}/`,
    {
      key: createNuxtDataKey(['one-on-one', oneOnOneId]),
    },
  );

export const useGetOneOnOneTags = () =>
  useApiFetch<Schema<'TagRead'>[]>('/value-tags/');
