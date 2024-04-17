import sanitizeHtml from 'sanitize-html';

export const extractHtmlContent = (htmlString: string) => {
  const textContentMatches = sanitizeHtml(htmlString).match(/<[^>]*>([^<]*)/g);

  const textContent = textContentMatches
    ?.map((match) => match.replace(/<[^>]*>/g, ''))
    .join(' ');

  return textContent;
};
