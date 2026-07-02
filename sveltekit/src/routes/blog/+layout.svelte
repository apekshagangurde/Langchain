<script lang="ts">
	let { children } = $props();

	const posts = ['hello-world', 'sveltekit-rocks'];
</script>

<div style="display: flex; gap: 2rem;">
	<aside>
		<h3>Posts</h3>
		<ul>
			{#each posts as slug}
				<li><a href="/blog/{slug}">{slug}</a></li>
			{/each}
		</ul>
	</aside>

	<div>
		{@render children()}
	</div>
</div>
