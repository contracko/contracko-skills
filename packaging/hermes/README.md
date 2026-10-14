# Contracko for Hermes

1. Extract the archive and run `hermes plugins install ./contracko-hermes --no-enable`.
2. Review and explicitly enable the `contracko` package.
3. Reuse an existing `mcp_servers.contracko` entry in `~/.hermes/config.yaml`. Otherwise, explicitly approve adding this entry, preserving the rest of the file:

   ```yaml
   mcp_servers:
     contracko:
       url: "https://app.contracko.com/mcp"
       auth: oauth
   ```

4. Run `hermes mcp login contracko`. The browser opens for the [sign-in and consent steps](https://github.com/contracko/contracko-skills#install).
5. Reload MCP or restart Hermes when connected.

Hermes namespaces the skills and keeps OAuth credentials in its native token store; enabling the package does not authenticate it.
