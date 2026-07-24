<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<nav>
	<a href="/" aria-current={page.url.pathname === '/'}>Home</a>
	<a href="/about" aria-current={page.url.pathname === '/about'}>About</a>
	<a href="/blog/hello-world">Blog: hello-world</a>
</nav>

<p>Current path: {page.url.pathname}</p>
<pre>page.params = {JSON.stringify(page.params)}
page.data   = {JSON.stringify(page.data)}</pre>
<p>Request ID (from hooks.server.ts via locals): {page.data.requestId}</p>

{@render children()}
