import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const posts: Record<string, string> = {
	'hello-world': 'This is my first post!',
	'sveltekit-rocks': 'Routing by folders is genuinely nice.'
};

export const load: PageServerLoad = ({ params }) => {
	const content = posts[params.slug];

	if (!content) {
		error(404, 'Post not found');
	}

	return {
		slug: params.slug,
		content
	};
};
