import dayjs from 'dayjs';
import 'dayjs/locale/fa';
import utc from 'dayjs/plugin/utc';
import jalaliday from 'jalaliday';

dayjs.extend(utc);
dayjs.extend(jalaliday);

export default dayjs;
