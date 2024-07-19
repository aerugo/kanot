export function clickOutside(node: HTMLElement, callback: () => void) {
  const handleClick = (event: MouseEvent) => {
    if (node && !node.contains(event.target as Node) && !event.defaultPrevented) {
      callback();
    }
  };

  document.addEventListener('click', handleClick, true);

  return {
    destroy() {
      document.removeEventListener('click', handleClick, true);
    }
  };
}

export function getDomain(url: string): string {
  if (!url) return '';
  try {
    const domain = new URL(url).hostname;
    // remove subdomain and toplevel domain
    const site = domain.split('.').slice(-2).join('.').split('.')[0];
    return site.replace('www.', '').toLowerCase();
  } catch (e) {
    return url;
  }
}

export function generateGoogleMapsLink(coordinateString: string): string {
  const coordinateRegex = /^-?\d+(\.\d+)?,-?\d+(\.\d+)?$/;
  const strippedCoordinateString = coordinateString.replace(/\s+/g, ''); // Remove all spaces
  if (coordinateRegex.test(strippedCoordinateString)) {
    const [latitude, longitude] = strippedCoordinateString.split(',');
    return `https://www.google.com/maps?q=${latitude},${longitude}`;
  } else {
    return '';
  }
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate: boolean = false
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return function(this: ThisParameterType<T>, ...args: Parameters<T>) {
    const context = this;

    const later = function() {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };

    const callNow = immediate && !timeout;
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);

    if (callNow) func.apply(context, args);
  };
}