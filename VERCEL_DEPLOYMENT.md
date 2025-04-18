# Deploying to Vercel

This guide will walk you through deploying your FinSight application to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. [Vercel CLI](https://vercel.com/docs/cli) (optional, for local testing)
3. A GitHub account (recommended for continuous deployment)

## Step 1: Prepare Your Repository

If you haven't already, push your code to a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/finsight.git
git push -u origin main
```

## Step 2: Set Up Vercel

### Using the Vercel Dashboard

1. Log in to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" > "Project"
3. Import your GitHub repository
4. Configure your project:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: Leave empty (Vercel will use the settings in vercel.json)
   - Output Directory: Leave empty

### Environment Variables

Add your environment variables in the Vercel dashboard:
- LLAMA_CLOUD_API_KEY
- OPENAI_API_KEY
- SESSION_SECRET

## Step 3: Deploy

Click "Deploy" and wait for the build to complete. Vercel will provide you with a deployment URL when finished.

## Step 4: Custom Domain (Optional)

1. In your project settings on Vercel, go to "Domains"
2. Add your custom domain and follow the instructions to configure DNS settings

## Troubleshooting

If you encounter any issues:

1. **Build Errors**: Check the build logs in the Vercel dashboard for specific errors
2. **Environment Variables**: Verify that all required environment variables are set correctly
3. **File Size Limits**: Ensure your PDFs don't exceed Vercel's payload limits (use client-side compression if needed)
4. **Timeouts**: For longer-running analyses, consider implementing a webhook pattern or progress indicator

### Fixing asyncio SyntaxError

If you encounter a SyntaxError related to `asyncio` and the `async` keyword, check:

1. The Python version on Vercel is set to 3.9+ in your `vercel.json`:
```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python@3.1.34",
      "config": { "runtime": "python3.9" }
    }
  ]
}
```

2. Ensure `asyncio` isn't listed as a separate dependency in requirements.txt (it's built into Python 3.9+)

3. Make sure `runtime.txt` contains `python-3.9`

## Local Testing with Vercel CLI (Optional)

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Test your deployment locally
vercel dev

# Deploy to production
vercel --prod
```

## Maintenance

After deploying:
1. Set up a custom domain for a professional look
2. Configure automatic deployments from your GitHub repository
3. Monitor usage and errors in the Vercel dashboard

Your deployment is now complete! Visit your Vercel deployment URL to access your application. 