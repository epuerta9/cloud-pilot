# cloud-pilot

vibe and fly with your infrastructure

## Development

Make sure you have the following environment variables set:

```bash
export ANTHROPIC_API_KEY=<your-anthropic-api-key>
export AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
```

Then run the following command to start the development frontend and backend:

```bash
docker compose up --build
```

## Development Workflow

### Development Mode with Hot Reloading

For a better development experience with hot reloading (changes reflect immediately without rebuilding):

```bash
# Start development environment with hot reloading
./dev.sh
```

This uses a special development configuration that:
- Mounts your local frontend code directly into the container
- Uses React's development server instead of Nginx
- Enables hot reloading so changes appear instantly in the browser
- Preserves node_modules in the container (faster builds)

### Production Deployment

When you're ready to deploy to production:

```bash
# Deploy to production
./deploy.sh
```

This builds optimized production containers with:
- Minified frontend build
- Nginx for serving static files
- Better performance for end users

### Making Frontend Changes

With development mode:
1. Start the environment with `./dev.sh`
2. Edit any frontend files in the `frontend/src` directory
3. Changes will automatically appear in the browser
4. No need to rebuild or restart containers
