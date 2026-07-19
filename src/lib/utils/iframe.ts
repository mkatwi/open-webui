const IFRAME_SRC_REGEX = /<iframe\b[^>]*\bsrc\s*=\s*(?:"([^"]+)"|'([^']+)'|([^'"\s>]+))/i;

const getBrowserBaseUrl = () =>
	typeof window !== 'undefined' && window.location?.href ? window.location.href : undefined;

export const isSafeGenericIframeSrc = (
	src: string,
	baseUrl: string | undefined = getBrowserBaseUrl()
) => {
	if (!src || !baseUrl) {
		return false;
	}

	try {
		const base = new URL(baseUrl);
		const url = new URL(src, base);

		return (url.protocol === 'https:' || url.protocol === 'http:') && url.origin !== base.origin;
	} catch {
		return false;
	}
};

export const getSafeGenericIframeSrc = (
	html: string,
	baseUrl: string | undefined = getBrowserBaseUrl()
) => {
	const match = html.match(IFRAME_SRC_REGEX);
	const src = match?.[1] ?? match?.[2] ?? match?.[3] ?? null;

	if (!src) {
		return null;
	}

	const normalizedSrc = src.replaceAll('&amp;', '&');
	return isSafeGenericIframeSrc(normalizedSrc, baseUrl) ? normalizedSrc : null;
};
