export function getVibeEmoji(
  vibe: Schema<'LeaderVibeEnum'> | Schema<'MemberVibeEnum'> | null | undefined,
) {
  if (!vibe) return '';

  return {
    ':)': '😊',
    ':|': '😐',
    ':(': '☹️',
  }[vibe];
}
