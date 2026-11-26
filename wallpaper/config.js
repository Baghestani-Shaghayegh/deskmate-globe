// Settings for the wallpaper. Edit, then rebuild:  python3 scripts/build_wallpaper.py
// Tip: add #demo (fake PC stats + privacy) or #reel (vertical 9:16 layout for phone videos) to the file's address.
window.DESKMATE_CONFIG = {
  // Your clock and weather. timezone: an IANA name like 'Europe/Paris', or 'auto' for this computer's timezone.
  // lat/lng: where to show the weather for (null = no weather). units: 'C' or 'F'.
  home: { timezone: 'auto', lat: null, lng: null, units: 'C' },

  // Someone far away (optional): their local time under yours, a glowing arc and two dots on the globe.
  // Example: { name: 'Mom', timezone: 'Asia/Tokyo', lat: 35.68, lng: 139.69 }
  partner: null,

  // Days-together counter with 100-day milestones and anniversaries (optional, dates as YYYY-MM-DD).
  // Example: { since: '2024-02-14', firstDate: '2023-12-01' }
  together: null,

  // Where the globe starts, e.g. { lat: 20, lng: 0 }. null = automatic.
  startView: null,
};
