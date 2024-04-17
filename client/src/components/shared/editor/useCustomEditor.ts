import { Link as TiptapLink } from '@tiptap/extension-link';
import { Underline as TiptapUnderline } from '@tiptap/extension-underline';
import TextDirection from 'tiptap-text-direction';
import type { EditorOptions } from '@tiptap/core';

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
      TextDirection.configure({
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
