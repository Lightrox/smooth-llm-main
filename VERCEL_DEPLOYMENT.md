# Vercel Deployment Guide for SmoothLLM

## 🚀 Quick Deployment Steps

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy from your project directory
```bash
vercel
```

### 4. Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? **Your account**
- Link to existing project? **No**
- What's your project's name? **smoothllm** (or any name you prefer)
- In which directory is your code located? **./** (current directory)

## 📁 Files Created for Vercel

- `vercel.json` - Vercel configuration
- `wsgi.py` - WSGI entry point for Flask
- `.vercelignore` - Files to exclude from deployment
- Updated `requirements.txt` - Added gunicorn
- Updated `app.py` - Fixed database path and Vercel compatibility

## ⚠️ Important Notes

### Database Limitations
- SQLite database is stored in `/tmp` directory on Vercel
- Data is **NOT persistent** between deployments
- For production, consider using a cloud database like:
  - Vercel Postgres
  - PlanetScale
  - Supabase
  - MongoDB Atlas

### Model Loading
- Large ML models are disabled on Vercel due to size limits
- The app will use mock responses when models aren't available
- For full functionality, consider:
  - Railway
  - Render
  - Google Cloud Run
  - AWS Lambda with larger memory

### Environment Variables
If you need to set environment variables:
```bash
vercel env add FLASK_ENV
vercel env add SECRET_KEY
```

## 🔧 Troubleshooting

### Common Issues:
1. **"Function not found"** - Make sure `wsgi.py` exists and is properly configured
2. **"Module not found"** - Check `requirements.txt` includes all dependencies
3. **"Database error"** - SQLite works but data isn't persistent
4. **"Timeout"** - Vercel has 10-second timeout for hobby plans

### Redeploy after changes:
```bash
vercel --prod
```

## 🌐 Access Your App
After deployment, Vercel will give you a URL like:
`https://smoothllm-xxx.vercel.app`

## 📊 Monitoring
- Check Vercel dashboard for logs and errors
- Monitor function execution time
- Check for memory usage issues

## 🔄 Alternative Deployments
For full functionality with models, consider:
- **Railway**: Better for ML apps
- **Render**: Good free tier
- **Google Cloud Run**: Scalable
- **AWS Lambda**: Serverless with more resources
