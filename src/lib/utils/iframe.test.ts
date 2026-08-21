import { describe, expect, it } from 'vitest';

import { getSafeIframeSrc } from './iframe';

describe('getSafeIframeSrc', () => {
	it('allows absolute external http and https iframe sources', () => {
		expect(
			getSafeIframeSrc('https://example.com/embed?id=1&amp;view=full', 'https://app.test')
		).toBe('https://example.com/embed?id=1&view=full');
		expect(getSafeIframeSrc('http://example.com/embed', 'http://app.test')).toBe(
			'http://example.com/embed'
		);
	});

	it('rejects relative and same-origin iframe sources', () => {
		expect(getSafeIframeSrc('/api/v1/auths/signout', 'https://app.test')).toBeNull();
		expect(
			getSafeIframeSrc('https://app.test/api/v1/auths/signout', 'https://app.test')
		).toBeNull();
	});

	it('rejects non-http iframe sources', () => {
		expect(getSafeIframeSrc('javascript:alert(1)', 'https://app.test')).toBeNull();
		expect(getSafeIframeSrc('data:text/html,<h1>bad</h1>', 'https://app.test')).toBeNull();
		expect(getSafeIframeSrc('', 'https://app.test')).toBeNull();
	});
});
