import { localize } from '@vee-validate/i18n';
import en from '@vee-validate/i18n/dist/locale/en.json';
import {
  email,
  required,
  max,
  min_value,
  max_value,
} from '@vee-validate/rules';
import { configure, defineRule } from 'vee-validate';

export default defineNuxtPlugin(() => {
  defineRule('email', email);
  defineRule('required', required);
  defineRule('max', max);
  defineRule('min_value', min_value);
  defineRule('max_value', max_value);

  const telRegexp = new RegExp(/^\+?\d{3,14}$/);
  defineRule('tel', (value: string) => value && telRegexp.test(value));

  configure({
    generateMessage: localize({ en }),
  });
});
