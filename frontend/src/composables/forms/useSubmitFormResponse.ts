import { useToast } from '@pey/core';

interface SubmitFormResponse {
  status?: string;
}

interface SubmitFormError {
  detail?: string;
}

interface SubmitFormPayload {
  responses: Record<string, string>;
  comment?: string;
}

export const useSubmitFormResponse = (formId: number) => {
  const { t } = useI18n();
  const toast = useToast();

  return useApiMutation<SubmitFormResponse, SubmitFormError, SubmitFormPayload>(
    `/forms/${formId}/submit/`,
    {
      method: 'POST',
      onSuccess: () => {
        toast.success({
          title: 'Form submitted successfully',
          message: '',
        });
      },
      onError: (error) => {
        toast.error({
          title: t('form.submitFormError'),
          message: error?.response?._data?.detail || '',
        });
      },
    },
  );
};
