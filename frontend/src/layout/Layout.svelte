<script>
  import { Link, useLocation } from "svelte-routing";

  const location = useLocation();
</script>

<div class="layout">
  <nav>
    <ul>
      <li class:active={$location.pathname === "/"}>
        <Link to="/">Home</Link>
      </li>
      <li class:active={$location.pathname === "/codes"}>
        <Link to="/codes">Codes</Link>
      </li>
      <li class:active={$location.pathname === "/content"}>
        <Link to="/content">Content</Link>
      </li>
    </ul>
  </nav>

  <main>
    <slot></slot>
  </main>

  <footer>
    <p>&copy; 2024 Kanot Code Management</p>
  </footer>
</div>

<style>
  .layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  nav {
    background-color: #3498db;
    padding: 1rem;
  }

  nav ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
    display: flex;
  }

  nav li {
    margin-right: 1rem;
  }

  :global(nav a) {
    color: white;
    text-decoration: none;
    font-weight: bold;
  }

  :global(nav li.active a) {
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