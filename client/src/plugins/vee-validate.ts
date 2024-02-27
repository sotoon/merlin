import { localize } from '@vee-validate/i18n';
import en from '@vee-validate/i18n/dist/locale/en.json';
import { email, required } from '@vee-validate/rules';
import { configure, defineRule } from 'vee-validate';

export default defineNuxtPlugin(() => {
  defineRule('email', email);
  defineRule('required', required);

  configure({
    generateMessage: localize({ en }),
  });
});
