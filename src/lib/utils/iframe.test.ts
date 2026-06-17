import { describe, expect, test } from 'vitest';

import { extractIframeSrc, getSafeIframeSrc } from './iframe';

describe('extractIframeSrc', () => {
	test('extracts double and single quoted iframe sources', () => {
		expect(extractIframeSrc('<iframe src="https://example.com/embed"></iframe>')).toBe(
			'https://example.com/embed'
		);
		expect(extractIframeSrc("<iframe title='demo' src='https://example.org/embed'></iframe>")).toBe(
			'https://example.org/embed'
		);
	});
});

describe('getSafeIframeSrc', () => {
	const origin = 'https://open-webui.example';

	test('blocks relative and same-origin iframe sources', () => {
		expect(getSafeIframeSrc('/api/v1/auths/signout', origin)).toBeNull();
		expect(getSafeIframeSrc('https://open-webui.example/api/v1/auths/signout', origin)).toBeNull();
	});

	test('blocks non-http iframe sources', () => {
		expect(getSafeIframeSrc('javascript:alert(1)', origin)).toBeNull();
		expect(getSafeIframeSrc('data:text/html,<h1>bad</h1>', origin)).toBeNull();
	});

	test('allows external http and https iframe sources', () => {
		expect(getSafeIframeSrc('https://example.com/embed?id=1', origin)).toBe(
			'https://example.com/embed?id=1'
		);
		expect(getSafeIframeSrc('http://example.com/embed', origin)).toBe('http://example.com/embed');
	});
});
