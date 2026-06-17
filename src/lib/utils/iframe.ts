const IFRAME_SRC_REGEX = /<iframe\s+[^>]*src=(?:"([^"]+)"|'([^']+)')[^>]*>\s*<\/iframe>/i;

export const extractIframeSrc = (html: string | null | undefined): string | null => {
	const match = html?.match(IFRAME_SRC_REGEX);

	return match ? (match[1] ?? match[2] ?? null) : null;
};

export const getSafeIframeSrc = (
	src: string | null | undefined,
	currentOrigin: string
): string | null => {
	const trimmedSrc = src?.trim();
	if (!trimmedSrc) {
		return null;
	}

	let url: URL;
	let origin: URL;
	try {
		url = new URL(trimmedSrc, currentOrigin);
		origin = new URL(currentOrigin);
	} catch {
		return null;
	}

	if (!['http:', 'https:'].includes(url.protocol)) {
		return null;
	}

	if (url.origin === origin.origin) {
		return null;
	}

	return url.href;
};
