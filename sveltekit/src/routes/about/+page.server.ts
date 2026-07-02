import type { PageServerLoad } from './$types';

export const load: PageServerLoad = () => {
	return {
		message: 'This data was loaded on the server before the page rendered.',
		time: new Date().toISOString()
	};
};
