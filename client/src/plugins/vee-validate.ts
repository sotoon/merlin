import { localize } from '@vee-validate/i18n';
import en from '@vee-validate/i18n/dist/locale/en.json';
import { email, required } from '@vee-validate/rules';
import { configure, defineRule } from 'vee-validate';

export default defineNuxtPlugin(() => {
  defineRule('email', email);
  defineRule('required', required);

  const telRegexp = new RegExp(/^\+\d{3,14}$/);
  defineRule('tel', (value: string) => value && telRegexp.test(value));

  configure({
    generateMessage: localize({ en }),
  });
});
