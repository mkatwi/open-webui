export const getSafeExternalIframeSrc = (src: string | null | undefined): string | null => {
	const value = src?.trim().replaceAll('&amp;', '&');

	if (!value) {
		return null;
	}

	try {
		const url = new URL(value);

		if (url.protocol !== 'https:' && url.protocol !== 'http:') {
			return null;
		}

		return url.href;
	} catch {
		return null;
	}
};
