export const extractTextFromHTML = (html: string) =>
  html.replace(/<[^>]*>|&[^;]+;/g, '');
