<script lang="ts">
	import { enhance } from '$app/forms';

	let { data, form } = $props();
</script>

<h1>Guestbook</h1>

<form method="POST" use:enhance>
	<input name="message" placeholder="Leave a message" />
	<button type="submit">Sign</button>
</form>

{#if form?.error}
	<p style="color: red;">{form.error}</p>
{/if}

<ul>
	{#each data.messages as message}
		<li>{message}</li>
	{/each}
</ul>
