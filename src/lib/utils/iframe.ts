const SAFE_IFRAME_PROTOCOLS = new Set(['http:', 'https:']);

export const getSafeIframeSrc = (
	src: string | null | undefined,
	currentOrigin = typeof window !== 'undefined' ? window.location.origin : undefined
): string | null => {
	const normalizedSrc = src?.replaceAll('&amp;', '&').trim();

	if (!normalizedSrc) {
		return null;
	}

	try {
		const url = new URL(normalizedSrc);

		if (!SAFE_IFRAME_PROTOCOLS.has(url.protocol)) {
			return null;
		}

		if (currentOrigin && url.origin === currentOrigin) {
			return null;
		}

		return url.href;
	} catch {
		return null;
	}
};
