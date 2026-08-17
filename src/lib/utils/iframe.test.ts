import { describe, expect, it } from 'vitest';

import { getSafeIframeSrc } from './iframe';

describe('getSafeIframeSrc', () => {
	const currentOrigin = 'https://chat.example.com';
	const webuiBaseUrl = 'https://api.example.com';

	it('allows external http and https iframe URLs', () => {
		expect(
			getSafeIframeSrc('https://videos.example.net/embed/123?autoplay=0', currentOrigin, webuiBaseUrl)
		).toBe('https://videos.example.net/embed/123?autoplay=0');
		expect(getSafeIframeSrc('http://legacy.example.net/embed', currentOrigin, webuiBaseUrl)).toBe(
			'http://legacy.example.net/embed'
		);
	});

	it('blocks relative and same-origin iframe URLs', () => {
		expect(getSafeIframeSrc('/api/v1/auths/signout', currentOrigin, webuiBaseUrl)).toBeNull();
		expect(getSafeIframeSrc('./api/v1/auths/signout', currentOrigin, webuiBaseUrl)).toBeNull();
		expect(
			getSafeIframeSrc('https://chat.example.com/api/v1/auths/signout', currentOrigin, webuiBaseUrl)
		).toBeNull();
	});

	it('blocks the configured WebUI backend origin', () => {
		expect(
			getSafeIframeSrc('https://api.example.com/api/v1/auths/signout', currentOrigin, webuiBaseUrl)
		).toBeNull();
	});

	it('blocks scriptable and local schemes', () => {
		expect(getSafeIframeSrc('javascript:alert(1)', currentOrigin, webuiBaseUrl)).toBeNull();
		expect(getSafeIframeSrc('data:text/html,<script>alert(1)</script>', currentOrigin, webuiBaseUrl)).toBeNull();
		expect(getSafeIframeSrc('file:///etc/passwd', currentOrigin, webuiBaseUrl)).toBeNull();
	});
});
