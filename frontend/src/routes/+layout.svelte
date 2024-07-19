<script>
	import { page } from '$app/stores';
</script>

<div class="layout">
	<nav>
		<a href="/" class:active={$page.url.pathname === '/'}>Home</a>
		<a href="/codes" class:active={$page.url.pathname === '/codes'}>Codes</a>
		<a href="/content" class:active={$page.url.pathname === '/content'}>Content</a>
	</nav>

	<main>
		<slot />
	</main>

	<footer>
		<p>&copy; 2024 Kanot Code Management</p>
	</footer>
</div>

<style>
	:global(body) {
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
		line-height: 1.6;
		color: #333;
		background-color: #f9f9f9;
		margin: 0;
		padding: 0;
	}

	.layout {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	nav {
		background-color: #3498db;
		padding: 1rem;
	}

	nav a {
		color: white;
		text-decoration: none;
		margin-right: 1rem;
		font-weight: bold;
	}

	nav a.active {
		text-decoration: underline;
	}

	main {
		flex: 1;
		padding: 2rem;
	}

	footer {
		background-color: #34495e;
		color: white;
		text-align: center;
		padding: 1rem;
	}
</style>
