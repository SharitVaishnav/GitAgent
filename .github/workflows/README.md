# Keep Backend Alive - GitHub Action

This GitHub Action prevents your Render backend from spinning down due to inactivity on the free tier.

## How It Works

- **Automatic Pings**: Runs every 10 minutes to ping your backend's `/health` endpoint
- **Prevents Sleep**: Keeps your Render service active and responsive
- **Manual Trigger**: Can be manually triggered from the GitHub Actions tab if needed

## Setup Instructions

### 1. Push to GitHub

First, commit and push this workflow to your repository:

```bash
git add .github/workflows/keep-backend-alive.yml
git commit -m "Add GitHub Action to keep backend alive"
git push origin main
```

### 2. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on the **"Actions"** tab
3. If prompted, click **"I understand my workflows, go ahead and enable them"**

### 3. Verify It's Working

After pushing, you can verify the workflow is active:

1. Go to **Actions** tab in your GitHub repository
2. You should see **"Keep Backend Alive"** in the workflows list
3. It will run automatically every 10 minutes
4. You can also click **"Run workflow"** to test it manually

## Monitoring

- Check the **Actions** tab to see the workflow runs
- Each run will show:
  - ✅ Success if backend responds with 200
  - ⚠️ Warning if backend returns a different status code
  - Timestamp of when the ping occurred

## Configuration

### Change Ping Frequency

Edit `.github/workflows/keep-backend-alive.yml` and modify the cron schedule:

```yaml
schedule:
  - cron: '*/10 * * * *'  # Every 10 minutes
  # - cron: '*/5 * * * *'   # Every 5 minutes (more aggressive)
  # - cron: '*/15 * * * *'  # Every 15 minutes (less frequent)
```

### Change Backend URL

If your backend URL changes, update the URL in the workflow file:

```yaml
curl -s -o /dev/null -w "%{http_code}" https://your-new-backend-url.onrender.com/health
```

## Important Notes

- ⏰ **Render Free Tier**: Spins down after 15 minutes of inactivity
- 🔄 **10-Minute Interval**: Ensures your backend stays active
- 💰 **Cost**: Completely free - GitHub Actions provides 2,000 minutes/month for free
- 🚀 **Cold Start**: If the backend does spin down, it takes 30+ seconds to restart

## Troubleshooting

### Workflow Not Running?

1. Check that GitHub Actions are enabled in your repository settings
2. Verify the workflow file is in `.github/workflows/` directory
3. Ensure the file has `.yml` or `.yaml` extension

### Backend Still Spinning Down?

1. Check the Actions tab to see if the workflow is running successfully
2. Verify the backend URL is correct
3. Ensure your `/health` endpoint is working (test it manually)
4. Consider reducing the interval to 5 minutes if needed

## Alternative Solutions

If you need more reliability:

1. **Upgrade Render Plan**: $7/month for always-on instances
2. **Use UptimeRobot**: Free external monitoring service
3. **Switch Hosting**: Consider Railway, Fly.io, or Koyeb with better free tiers
