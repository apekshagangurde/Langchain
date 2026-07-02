import type { Actions, PageServerLoad } from './$types';

const messages: string[] = ['Welcome to the guestbook!'];

export const load: PageServerLoad = () => {
	return { messages };
};

export const actions: Actions = {
	default: async ({ request }) => {
		const data = await request.formData();
		const message = data.get('message');

		if (typeof message !== 'string' || message.trim() === '') {
			return { error: 'Message cannot be empty' };
		}

		messages.push(message.trim());

		return { success: true };
	}
};
