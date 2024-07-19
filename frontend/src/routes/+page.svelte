<svelte:head>
  <title>Welcome to Kanot Code Management</title>
</svelte:head>

<h1>Welcome to Kanot Code Management</h1>
<p>Use the navigation to manage your codes and content.</p>
<div class="links">
  <a href="/codes" class="button">Go to Codes</a>
  <a href="/content" class="button">Go to Content</a>
</div>


<style>
  h1 {
    color: #2c3e50;
    text-align: center;
  }

  p {
    text-align: center;
  }

  .links {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 2rem;
  }

  .button {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #3498db;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.3s ease;
  }
  .button:hover {
    background-color: #2980b9;
  }
</style>