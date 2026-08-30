/* Care Plus - Main Interactive Client JavaScript */

document.addEventListener('DOMContentLoaded', () => {
  const appSettingsElement = document.getElementById('appSettings');
  let appSettings = { theme: 'light', timezone: 'Asia/Colombo' };
  if (appSettingsElement) {
    try { appSettings = JSON.parse(appSettingsElement.textContent); } catch (error) { /* use defaults */ }
  }

  const themeToggle = document.getElementById('themeToggle');
  const themeToggleIcon = document.getElementById('themeToggleIcon');
  const themeToggleText = document.getElementById('themeToggleText');
  const applyTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    if (themeToggleIcon) themeToggleIcon.dataset.theme = theme;
    if (themeToggleText) themeToggleText.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
  };
  applyTheme(appSettings.theme);
  if (themeToggle) themeToggle.addEventListener('click', async () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(theme);
    const formData = new FormData();
    formData.append('theme', theme);
    await fetch('/profile/theme', { method: 'POST', body: formData });
  });

  const sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebarToggle) sidebarToggle.addEventListener('click', () => {
    document.body.classList.toggle('sidebar-open');
  });

  const realWorldTime = () => {
    const parts = new Intl.DateTimeFormat('en-GB', {
      timeZone: appSettings.timezone,
      hour: '2-digit', minute: '2-digit', hour12: false
    }).formatToParts(new Date());
    const hour = parts.find((part) => part.type === 'hour').value;
    const minute = parts.find((part) => part.type === 'minute').value;
    return `${hour}:${minute}`;
  };
  // Food Image Upload Preview
  const foodImageInput = document.getElementById('foodImageInput');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');
  const imagePreview = document.getElementById('imagePreview');
  const fileInputText = document.getElementById('fileInputText');

  if (foodImageInput && imagePreview) {
    foodImageInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const allowed = ['image/jpeg', 'image/png', 'image/webp'];
      if (!allowed.includes(file.type)) {
        if (fileInputText) fileInputText.textContent = 'Invalid format — use JPG, PNG or WEBP';
        foodImageInput.value = '';
        if (imagePreviewContainer) imagePreviewContainer.style.display = 'none';
        return;
      }
      if (fileInputText) fileInputText.textContent = file.name;
      const reader = new FileReader();
      reader.onload = (event) => {
        imagePreview.src = event.target.result;
        if (imagePreviewContainer) imagePreviewContainer.style.display = 'block';
      };
      reader.readAsDataURL(file);
    });
  }

  // Dynamic Portion Size Nutrition Calculator on Food Recognition Page
  const portionInput = document.getElementById('serving_amount_g');
  if (portionInput) {
    const baseCals = parseFloat(portionInput.dataset.baseCals || 0);
    const baseProt = parseFloat(portionInput.dataset.baseProt || 0);
    const baseCarbs = parseFloat(portionInput.dataset.baseCarbs || 0);
    const baseFat = parseFloat(portionInput.dataset.baseFat || 0);
    const baseFibre = parseFloat(portionInput.dataset.baseFibre || 0);
    const baseSugar = parseFloat(portionInput.dataset.baseSugar || 0);

    const calcCals = document.getElementById('calc_cals');
    const calcProt = document.getElementById('calc_prot');
    const calcCarbs = document.getElementById('calc_carbs');
    const calcFat = document.getElementById('calc_fat');
    const calcFibre = document.getElementById('calc_fibre');
    const calcSugar = document.getElementById('calc_sugar');

    const updateCalculatedNutrition = () => {
      const grams = parseFloat(portionInput.value) || 100.0;
      const mult = grams / 100.0;

      if (calcCals) calcCals.textContent = (baseCals * mult).toFixed(1) + ' kcal';
      if (calcProt) calcProt.textContent = (baseProt * mult).toFixed(1) + ' g';
      if (calcCarbs) calcCarbs.textContent = (baseCarbs * mult).toFixed(1) + ' g';
      if (calcFat) calcFat.textContent = (baseFat * mult).toFixed(1) + ' g';
      if (calcFibre) calcFibre.textContent = (baseFibre * mult).toFixed(1) + ' g';
      if (calcSugar) calcSugar.textContent = (baseSugar * mult).toFixed(1) + ' g';
    };

    portionInput.addEventListener('input', updateCalculatedNutrition);
  }

  const medicationReminderData = document.getElementById('medicationReminderData');
  let scheduledMedications = [];
  if (medicationReminderData) {
    try { scheduledMedications = JSON.parse(medicationReminderData.textContent); } catch (error) { scheduledMedications = []; }
  }
  const reminderPopup = document.getElementById('medicationReminderPopup');
  const reminderTitle = document.getElementById('medicationReminderTitle');
  const reminderMessage = document.getElementById('medicationReminderMessage');
  const dismissReminder = document.getElementById('dismissMedicationReminder');

  if (scheduledMedications.length && reminderPopup) {
    const medStorageKey = 'carePlusDismissedMedReminders';
    let dismissedMedReminders = {};
    try {
      dismissedMedReminders = JSON.parse(localStorage.getItem(medStorageKey) || '{}');
    } catch (error) {
      dismissedMedReminders = {};
    }
    const localClock = document.getElementById('localClock');

    const normalizeScheduledTime = (timeValue) => {
      const value = (timeValue || '').trim().toUpperCase();
      const match = value.match(/^(\d{1,2}):(\d{2})(?:\s*(AM|PM))?$/);
      if (!match) return '';

      let hours = Number(match[1]);
      const minutes = match[2];
      const meridiem = match[3];
      if (meridiem) {
        if (hours === 12) hours = 0;
        if (meridiem === 'PM') hours += 12;
      }
      if (hours > 23 || Number(minutes) > 59) return '';
      return `${String(hours).padStart(2, '0')}:${minutes}`;
    };

    const showMedicationReminder = (medication) => {
      const name = medication.name || 'your medication';
      reminderTitle.textContent = 'Medication reminder';
      reminderMessage.textContent = `It is time to take ${name}.`;
      reminderPopup.style.display = 'block';

      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Care Plus medication reminder', { body: `It is time to take ${name}.` });
      }
    };

    const checkMedicationTimes = () => {
      const now = new Date();
      const currentTime = realWorldTime();
      const todayParts = new Intl.DateTimeFormat('en-CA', { timeZone: appSettings.timezone }).format(now);
      const today = todayParts;
      if (localClock) localClock.textContent = `${currentTime} (${appSettings.timezone})`;

      scheduledMedications.forEach((medication) => {
        const scheduledTime = normalizeScheduledTime(medication.time);
        const reminderKey = `${today}-${medication.id}-${scheduledTime}`;
        if (scheduledTime === currentTime && !dismissedMedReminders[reminderKey]) {
          dismissedMedReminders[reminderKey] = true;
          localStorage.setItem(medStorageKey, JSON.stringify(dismissedMedReminders));
          showMedicationReminder(medication);
        }
      });
    };

    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().catch(() => {});
    }
    if (dismissReminder) dismissReminder.addEventListener('click', () => { reminderPopup.style.display = 'none'; });
    checkMedicationTimes();
    window.setInterval(checkMedicationTimes, 15000);
  }

  const wellnessReminderData = document.getElementById('wellnessReminderData');
  const wellnessReminderPopup = document.getElementById('wellnessReminderPopup');
  const dismissWellnessReminder = document.getElementById('dismissWellnessReminder');
  if (wellnessReminderData && wellnessReminderPopup) {
    let wellnessReminders = [];
    try { wellnessReminders = JSON.parse(wellnessReminderData.textContent); } catch (error) { wellnessReminders = []; }
    const wellnessStorageKey = 'carePlusDismissedWellnessReminders';
    let dismissedWellnessReminders = {};
    try {
      dismissedWellnessReminders = JSON.parse(localStorage.getItem(wellnessStorageKey) || '{}');
    } catch (error) {
      dismissedWellnessReminders = {};
    }
    const wellnessTitle = document.getElementById('wellnessReminderTitle');
    const wellnessMessage = document.getElementById('wellnessReminderMessage');

    const checkWellnessReminders = () => {
      const currentTime = realWorldTime();
      const today = new Intl.DateTimeFormat('en-CA', { timeZone: appSettings.timezone }).format(new Date());
      wellnessReminders.forEach((reminder) => {
        const reminderKey = `${today}-${reminder.id}-${reminder.time}`;
        if (reminder.time === currentTime && !dismissedWellnessReminders[reminderKey]) {
          wellnessTitle.textContent = 'Wellness reminder';
          wellnessMessage.textContent = `Time for ${reminder.name}.`;
          wellnessReminderPopup.style.display = 'block';
          dismissedWellnessReminders[reminderKey] = true;
          localStorage.setItem(wellnessStorageKey, JSON.stringify(dismissedWellnessReminders));
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Care Plus wellness reminder', { body: `Time for ${reminder.name}.` });
          }
        }
      });
    };

    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().catch(() => {});
    }
    if (dismissWellnessReminder) dismissWellnessReminder.addEventListener('click', () => { wellnessReminderPopup.style.display = 'none'; });
    checkWellnessReminders();
    window.setInterval(checkWellnessReminders, 15000);
  }
});
