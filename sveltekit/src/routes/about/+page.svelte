<script lang="ts">
	let { data } = $props();
</script>

<h1>About</h1>
<p>{data.message}</p>
<p>Loaded at: {data.time}</p>
