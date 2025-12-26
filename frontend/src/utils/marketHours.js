/**
 * Market Hours Utility
 * Determines if US stock market is open and provides related information
 */

/**
 * Check if US stock market is currently open
 * NYSE/NASDAQ hours: 9:30 AM - 4:00 PM ET, Monday-Friday (excluding holidays)
 */
export const isMarketOpen = () => {
  const now = new Date();

  // Convert to ET (UTC-5 or UTC-4 depending on DST)
  const etTime = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));

  // Get day of week (0 = Sunday, 6 = Saturday)
  const dayOfWeek = etTime.getDay();

  // Market closed on weekends
  if (dayOfWeek === 0 || dayOfWeek === 6) {
    return false;
  }

  // Get hours and minutes in ET
  const hours = etTime.getHours();
  const minutes = etTime.getMinutes();
  const totalMinutes = hours * 60 + minutes;

  // Market hours: 9:30 AM (570 minutes) to 4:00 PM (960 minutes)
  const marketOpen = 9 * 60 + 30;  // 9:30 AM
  const marketClose = 16 * 60;      // 4:00 PM

  return totalMinutes >= marketOpen && totalMinutes < marketClose;
};

/**
 * Get next market open time
 */
export const getNextMarketOpen = () => {
  const now = new Date();
  const etTime = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));

  const dayOfWeek = etTime.getDay();
  const hours = etTime.getHours();
  const minutes = etTime.getMinutes();
  const totalMinutes = hours * 60 + minutes;

  let nextOpen = new Date(etTime);

  // If it's weekend, next open is Monday
  if (dayOfWeek === 0) { // Sunday
    nextOpen.setDate(nextOpen.getDate() + 1);
    nextOpen.setHours(9, 30, 0, 0);
  } else if (dayOfWeek === 6) { // Saturday
    nextOpen.setDate(nextOpen.getDate() + 2);
    nextOpen.setHours(9, 30, 0, 0);
  } else {
    // Weekday
    const marketOpen = 9 * 60 + 30;
    const marketClose = 16 * 60;

    if (totalMinutes < marketOpen) {
      // Before market open today
      nextOpen.setHours(9, 30, 0, 0);
    } else if (totalMinutes >= marketClose) {
      // After market close - next open is tomorrow (or Monday if Friday)
      if (dayOfWeek === 5) { // Friday
        nextOpen.setDate(nextOpen.getDate() + 3); // Monday
      } else {
        nextOpen.setDate(nextOpen.getDate() + 1); // Tomorrow
      }
      nextOpen.setHours(9, 30, 0, 0);
    }
  }

  return nextOpen;
};

/**
 * Get next market close time
 */
export const getNextMarketClose = () => {
  const now = new Date();
  const etTime = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));

  const dayOfWeek = etTime.getDay();
  const hours = etTime.getHours();

  // If market is open, return today's close
  if (isMarketOpen()) {
    const nextClose = new Date(etTime);
    nextClose.setHours(16, 0, 0, 0);
    return nextClose;
  }

  // Market is closed, return next market day's close
  const nextOpen = getNextMarketOpen();
  const nextClose = new Date(nextOpen);
  nextClose.setHours(16, 0, 0, 0);
  return nextClose;
};

/**
 * Format time until next market event
 */
export const getTimeUntilMarketEvent = () => {
  const now = new Date();
  const isOpen = isMarketOpen();

  let targetTime;
  let eventType;

  if (isOpen) {
    targetTime = getNextMarketClose();
    eventType = 'close';
  } else {
    targetTime = getNextMarketOpen();
    eventType = 'open';
  }

  const diff = targetTime - now;

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  return {
    isOpen,
    eventType,
    hours,
    minutes,
    formatted: `${hours}h ${minutes}m`
  };
};

/**
 * Get market status object
 */
export const getMarketStatus = () => {
  const isOpen = isMarketOpen();
  const timeInfo = getTimeUntilMarketEvent();

  return {
    isOpen,
    status: isOpen ? 'OPEN' : 'CLOSED',
    message: isOpen
      ? `Market closes in ${timeInfo.formatted}`
      : `Market opens in ${timeInfo.formatted}`,
    nextEvent: isOpen ? 'close' : 'open',
    timeUntilEvent: timeInfo.formatted,
    hours: timeInfo.hours,
    minutes: timeInfo.minutes
  };
};
