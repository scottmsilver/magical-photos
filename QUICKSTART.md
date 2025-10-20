# Quick Start Guide 🚀

Get your Harry Potter style animated portraits in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Google API key ready (get from https://ai.google.dev/)
- [ ] A photo to animate

## Installation Steps

### 1. Set Up Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your key
# GOOGLE_API_KEY=your_actual_key_here
```

### 4. Run Your First Animation!

```bash
python examples/single_photo_example.py path/to/your/photo.jpg
```

That's it! Your animated video will be saved in the same directory as your photo.

## Common First-Time Issues

### "GOOGLE_API_KEY not found"
**Solution**: Make sure you created `.env` file and added your API key:
```bash
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### "venv: command not found"
**Solution**: Use `python3 -m venv` instead of just `venv`

### "Image file not found"
**Solution**: Use the full path to your image:
```bash
python examples/single_photo_example.py /full/path/to/photo.jpg
```

## Next Steps

Once you have your first animation:

1. Try different intensities:
   ```bash
   python examples/single_photo_example.py photo.jpg --intensity moderate
   ```

2. Adjust duration:
   ```bash
   python examples/single_photo_example.py photo.jpg --duration 5
   ```

3. Try different photo types:
   ```bash
   python examples/single_photo_example.py family.jpg --photo-type group
   ```

4. Read the full README.md for all features

## Getting Help

- **Full documentation**: See README.md
- **Development guide**: See AGENTS.md
- **Project plan**: See PLAN.md

Happy animating! ✨
