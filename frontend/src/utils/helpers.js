export function getDomain(url) {
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

export function generateGoogleMapsLink(coordinateString) {
    const coordinateRegex = /^-?\d+(\.\d+)?,-?\d+(\.\d+)?$/;
    const strippedCoordinateString = coordinateString.replace(/\s+/g, ''); // Remove all spaces
    if (coordinateRegex.test(strippedCoordinateString)) {
        const [latitude, longitude] = strippedCoordinateString.split(',');
        return `https://www.google.com/maps?q=${latitude},${longitude}`;
    } else {
        return '';
    }
}

export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}