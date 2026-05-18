import { describe, expect, it } from 'vitest';

import { getImageCompressionDimensions } from './index';

describe('getImageCompressionDimensions', () => {
	it('uses admin image compression dimensions when user compression is disabled', () => {
		expect(
			getImageCompressionDimensions(
				{ imageCompression: false },
				{ image_compression: { width: 1024, height: 768 } }
			)
		).toEqual({ width: 1024, height: 768 });
	});

	it('caps user image compression dimensions with configured limits', () => {
		expect(
			getImageCompressionDimensions(
				{ imageCompression: true, imageCompressionSize: { width: '2048', height: '500' } },
				{ image_compression: { width: 1024, height: 768 } }
			)
		).toEqual({ width: 1024, height: 500 });
	});

	it('preserves user dimensions for axes without configured limits', () => {
		expect(
			getImageCompressionDimensions(
				{ imageCompression: true, imageCompressionSize: { width: '2048', height: '600' } },
				{ image_compression: { width: 1024, height: null } }
			)
		).toEqual({ width: 1024, height: 600 });
	});

	it('ignores empty or non-positive dimensions', () => {
		expect(
			getImageCompressionDimensions(
				{ imageCompression: true, imageCompressionSize: { width: '', height: '0' } },
				{ image_compression: { width: '', height: -1 } }
			)
		).toEqual({ width: null, height: null });
	});
});
