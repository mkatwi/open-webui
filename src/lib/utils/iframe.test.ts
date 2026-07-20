import { describe, expect, it } from 'vitest';

import { getSafeExternalIframeSrc } from './iframe';

describe('getSafeExternalIframeSrc', () => {
	it('allows absolute http and https iframe sources', () => {
		expect(getSafeExternalIframeSrc('https://example.com/embed?id=1&amp;v=2')).toBe(
			'https://example.com/embed?id=1&v=2'
		);
		expect(getSafeExternalIframeSrc('http://example.com/embed')).toBe('http://example.com/embed');
	});

	it('blocks same-origin, script, data, and empty iframe sources', () => {
		expect(getSafeExternalIframeSrc('/api/v1/auths/signout')).toBeNull();
		expect(getSafeExternalIframeSrc('//example.com/embed')).toBeNull();
		expect(getSafeExternalIframeSrc('javascript:alert(1)')).toBeNull();
		expect(getSafeExternalIframeSrc('data:text/html,<script>alert(1)</script>')).toBeNull();
		expect(getSafeExternalIframeSrc('')).toBeNull();
	});
});
