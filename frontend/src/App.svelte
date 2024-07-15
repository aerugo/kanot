<script>
    import { Link, Route, Router } from "svelte-routing";
    import Layout from "./layout/Layout.svelte";
    import Codes from "./routes/Codes.svelte";
  
    export let url = "";
  </script>
  
  <Router {url}>
    <Layout>
      <Route path="codes" component={Codes} />
      <Route path="/">
        <h1>Welcome to Kanot Code Management</h1>
        <p>Use the navigation to manage your codes.</p>
        <Link to="/codes">Go to Codes</Link>
      </Route>
    </Layout>
  </Router>
  
  <style>
    :global(body) {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      line-height: 1.6;
      color: #333;
      background-color: #f9f9f9;
      margin: 0;
      padding: 0;
    }
  
    h1 {
      color: #2c3e50;
      text-align: center;
    }
  
    p {
      text-align: center;
    }
  </style>