import type { EditorOptions } from '@tiptap/core';

import { Link as TiptapLink } from '@tiptap/extension-link';
import { Table as TiptapTable } from '@tiptap/extension-table';
import { TableCell as TiptapTableCell } from '@tiptap/extension-table-cell';
import { TableHeader as TiptapTableHeader } from '@tiptap/extension-table-header';
import { TableRow as TiptapTableRow } from '@tiptap/extension-table-row';
import { Underline as TiptapUnderline } from '@tiptap/extension-underline';
import { TextDirection as TiptapTextDirection } from 'tiptap-text-direction';

export const useCustomEditor = (options: Partial<EditorOptions> = {}) => {
  const editor = useEditor({
    ...options,
    extensions: [
      TiptapStarterKit,
      TiptapUnderline,
      TiptapLink.extend({
        inclusive: false,
      }).configure({
        openOnClick: 'whenNotEditable',
      }),
      TiptapTable.configure({
        resizable: true,
      }),
      TiptapTableRow,
      TiptapTableHeader,
      TiptapTableCell,
      TiptapTextDirection.configure({
        types: [
          'heading',
          'paragraph',
          'blockquote',
          'bulletList',
          'orderedList',
          'codeBlock',
        ],
      }),
      ...(options.extensions || []),
    ],
  });

  onBeforeUnmount(() => {
    editor.value?.destroy();
  });

  return editor;
};
