# Netlify Deployment Guide for SmoothLLM

## 🚀 Quick Deployment Steps

### Method 1: Deploy via Netlify UI (Recommended)

1. **Go to [netlify.com](https://netlify.com)** and sign up/login
2. **Click "New site from Git"**
3. **Connect your GitHub repository**
4. **Configure build settings:**
   - Build command: `chmod +x build.sh && ./build.sh`
   - Publish directory: `.`
   - Python version: `3.9`
5. **Click "Deploy site"**

### Method 2: Deploy via Netlify CLI

1. **Install Netlify CLI:**
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify:**
   ```bash
   netlify login
   ```

3. **Deploy from your project directory:**
   ```bash
   netlify deploy
   ```

4. **For production deployment:**
   ```bash
   netlify deploy --prod
   ```

## 📁 Files Created for Netlify

- ✅ `netlify.toml` - Netlify configuration
- ✅ `runtime.txt` - Python version specification
- ✅ `Procfile` - Process file for web server
- ✅ `build.sh` - Build script
- ✅ `requirements.txt` - Lightweight dependencies
- ✅ Updated `app.py` - Removed heavy ML dependencies

## ⚙️ Configuration Details

### Build Settings
- **Build Command**: `chmod +x build.sh && ./build.sh`
- **Publish Directory**: `.` (root)
- **Python Version**: 3.9.18

### Environment Variables (Optional)
If you need to set environment variables in Netlify:
1. Go to Site Settings → Environment Variables
2. Add variables like:
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = `your-secret-key`

## 🔧 Features Available

### ✅ Working Features
- User authentication (sign up/sign in)
- User profiles and statistics
- Prompt analysis (mock responses)
- Prompt history storage
- Cross-device login
- Responsive web interface

### ⚠️ Limitations
- **Mock Analysis**: Uses keyword-based analysis instead of ML models
- **Database**: SQLite database (data may not persist between deployments)
- **No ML Models**: Heavy ML dependencies removed for deployment

## 🌐 Access Your App

After deployment, Netlify will give you a URL like:
`https://your-app-name.netlify.app`

## 🔄 Updating Your App

1. **Make changes to your code**
2. **Commit and push to GitHub**
3. **Netlify will automatically redeploy** (if auto-deploy is enabled)
4. **Or manually trigger deployment** in Netlify dashboard

## 📊 Monitoring

- **Netlify Dashboard**: Check build logs and deployment status
- **Function Logs**: Monitor serverless function execution
- **Analytics**: View site traffic and performance

## 🚨 Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check build logs in Netlify dashboard
   - Ensure all files are committed to Git
   - Verify Python version compatibility

2. **App Not Loading**
   - Check function logs
   - Verify all dependencies are in requirements.txt
   - Ensure app.py is in the root directory

3. **Database Issues**
   - SQLite works but data may not persist
   - Consider upgrading to a cloud database for production

4. **Function Timeout**
   - Netlify has timeout limits
   - Optimize your code for faster execution

### Debug Commands:
```bash
# Check local build
./build.sh

# Test locally
python app.py

# Check Netlify logs
netlify logs
```

## 🔄 Alternative Deployments

For full ML functionality, consider:
- **Railway**: Better for Python apps with ML
- **Render**: Good free tier with more resources
- **Google Cloud Run**: Scalable container deployment
- **Heroku**: Traditional web app hosting

## 📝 Notes

- The app uses mock analysis for prompt safety detection
- User accounts and history are stored in SQLite
- All core features work except for actual ML model inference
- Perfect for demonstration and testing purposes
