import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	console.log(`[${new Date().toISOString()}] ${event.request.method} ${event.url.pathname}`);

	event.locals.requestId = crypto.randomUUID();

	const response = await resolve(event);

	response.headers.set('x-request-id', event.locals.requestId);

	return response;
};
