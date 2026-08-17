const DEFAULT_BASE_ORIGIN = 'https://open-webui.invalid';

const getOrigin = (value: string | undefined, base: URL) => {
	if (!value) {
		return null;
	}

	try {
		return new URL(value, base).origin;
	} catch {
		return null;
	}
};

export const getSafeIframeSrc = (
	src: string | null | undefined,
	currentOrigin = globalThis.location?.origin ?? DEFAULT_BASE_ORIGIN,
	webuiBaseUrl = ''
) => {
	const trimmedSrc = src?.trim();
	if (!trimmedSrc) {
		return null;
	}

	let base: URL;
	let parsed: URL;
	try {
		base = new URL(currentOrigin || DEFAULT_BASE_ORIGIN);
		parsed = new URL(trimmedSrc, base);
	} catch {
		return null;
	}

	if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
		return null;
	}

	const blockedOrigins = new Set([base.origin]);
	const webuiOrigin = getOrigin(webuiBaseUrl, base);
	if (webuiOrigin) {
		blockedOrigins.add(webuiOrigin);
	}

	if (blockedOrigins.has(parsed.origin)) {
		return null;
	}

	return parsed.href;
};
