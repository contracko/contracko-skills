# Contracko for OpenClaw

1. Extract the archive and run `openclaw plugins install ./contracko-openclaw`.
2. Enable the bundle and restart the Gateway if prompted.
3. Reuse an existing `contracko` MCP entry. Otherwise, explicitly approve adding it to OpenClaw's central registry, then run:

   ```bash
   openclaw mcp set contracko '{"url":"https://app.contracko.com/mcp","transport":"streamable-http"}'
   openclaw mcp configure contracko --auth oauth
   openclaw mcp login contracko
   ```

The login command opens a browser. Follow the [sign-in and consent steps](https://github.com/contracko/contracko-skills#install). OpenClaw stores its own OAuth configuration and credentials; installing the bundle does not authenticate it.
