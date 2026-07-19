import { describe, expect, test } from 'vitest';

import { getSafeGenericIframeSrc, isSafeGenericIframeSrc } from './iframe';

const BASE_URL = 'https://openwebui.example.com/chat';

describe('generic iframe source validation', () => {
	test('blocks same-origin endpoints', () => {
		expect(isSafeGenericIframeSrc('/api/v1/auths/signout', BASE_URL)).toBe(false);
		expect(
			getSafeGenericIframeSrc('<iframe src="/api/v1/auths/signout"></iframe>', BASE_URL)
		).toBeNull();
	});

	test('blocks script and data URLs', () => {
		expect(isSafeGenericIframeSrc('javascript:alert(1)', BASE_URL)).toBe(false);
		expect(isSafeGenericIframeSrc('data:text/html,<h1>owned</h1>', BASE_URL)).toBe(false);
	});

	test('allows external http and https iframe URLs', () => {
		expect(isSafeGenericIframeSrc('https://widgets.example.net/embed', BASE_URL)).toBe(true);
		expect(
			getSafeGenericIframeSrc(
				'<iframe src="https://widgets.example.net/embed?x=1&amp;y=2"></iframe>',
				BASE_URL
			)
		).toBe('https://widgets.example.net/embed?x=1&y=2');
	});
});
