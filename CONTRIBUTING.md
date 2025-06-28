# Contributing to M3U8 Video Downloader

Thank you for your interest in contributing to the M3U8 Video Downloader project! 🎉

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a new branch for your feature
4. **Make** your changes
5. **Test** thoroughly
6. **Submit** a pull request

## 📋 Ways to Contribute

### 🐛 Bug Reports
Found a bug? Help us fix it!

**Before reporting:**
- Check if the issue already exists in [Issues](../issues)
- Test with the latest version
- Gather relevant information

**When reporting include:**
- Operating system and version
- Python version (if running from source)
- Steps to reproduce the issue
- Expected vs actual behavior
- Error messages or screenshots
- Sample M3U8 URL (if safe to share)

### 💡 Feature Requests
Have an idea for improvement?

**Before requesting:**
- Check existing [Issues](../issues) and [Discussions](../discussions)
- Consider if it fits the project's scope
- Think about implementation complexity

**When requesting include:**
- Clear description of the feature
- Use case and benefits
- Possible implementation approach
- Screenshots or mockups (if applicable)

### 🔧 Code Contributions

#### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/m3u8-downloader.git
cd m3u8-downloader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest flake8 black

# Run the application
python app.py
```

#### Code Style
- **Python Style**: Follow PEP 8 guidelines
- **Line Length**: Maximum 88 characters (Black formatter default)
- **Comments**: Write clear, concise comments for complex logic
- **Docstrings**: Use Google-style docstrings for functions and classes

#### Code Formatting
```bash
# Format code with Black
black app.py

# Check style with Flake8
flake8 app.py

# Type checking (optional)
mypy app.py
```

#### Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### 📝 Documentation
Help improve our documentation!

- Fix typos or unclear instructions
- Add examples or use cases
- Improve code comments
- Translate documentation
- Create video tutorials

## 🔀 Pull Request Process

### Before Submitting
1. **Test** your changes thoroughly
2. **Format** code according to style guidelines
3. **Update** documentation if needed
4. **Add** tests for new functionality
5. **Check** that all tests pass

### Pull Request Guidelines
1. **Clear Title**: Describe what the PR does
2. **Detailed Description**: Explain the changes and why
3. **Link Issues**: Reference related issues with `Fixes #123`
4. **Screenshots**: Include for UI changes
5. **Testing**: Describe how you tested the changes

### Example PR Description
```markdown
## Description
Adds support for custom FFmpeg path configuration

## Changes
- Added FFmpeg path setting in GUI
- Updated path detection logic
- Added configuration persistence
- Updated documentation

## Testing
- Tested on Windows 10 with custom FFmpeg installation
- Verified path persistence across app restarts
- Tested fallback to system PATH when custom path fails

## Screenshots
[Include screenshots of new UI elements]

Fixes #42
```

## 🏗️ Development Guidelines

### Project Structure
```
app.py              # Main GUI application
m3u8vi.py          # CLI reference implementation  
build.py           # Build script for executables
requirements.txt   # Python dependencies
tests/             # Test files
docs/              # Documentation
.github/           # GitHub workflows and templates
```

### Coding Best Practices

#### Error Handling
```python
# Good: Specific exception handling
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.Timeout:
    log_callback("Connection timeout occurred")
except requests.exceptions.HTTPError as e:
    log_callback(f"HTTP error: {e.response.status_code}")
```

#### Logging
```python
# Good: Informative logging
log_callback(f"Downloading segment {i+1}/{total_segments}: {filename}")

# Avoid: Generic messages
log_callback("Processing...")
```

#### GUI Threading
```python
# Good: Thread-safe GUI updates
def update_gui():
    self.progress_label.config(text=f"Progress: {percent}%")

self.after(0, update_gui)  # Schedule on main thread
```

### Adding New Features

#### GUI Features
1. **Design**: Consider user experience and accessibility
2. **Threading**: Ensure UI remains responsive
3. **Error Handling**: Provide clear user feedback
4. **Testing**: Test on multiple platforms if possible

#### Core Features
1. **Backwards Compatibility**: Avoid breaking existing functionality
2. **Performance**: Consider impact on download speed
3. **Cross-Platform**: Test on Windows, macOS, and Linux
4. **Documentation**: Update README and code comments

## 🧪 Testing

### Manual Testing Checklist
- [ ] GUI loads without errors
- [ ] Can enter M3U8 URLs
- [ ] Download process starts correctly
- [ ] Progress updates work
- [ ] File saves to chosen location
- [ ] Error messages are helpful
- [ ] App closes cleanly

### Platform Testing
- [ ] Windows 10/11
- [ ] macOS (latest)
- [ ] Linux (Ubuntu/Debian)

### Test Cases
- [ ] Valid M3U8 URLs
- [ ] Invalid URLs
- [ ] Network interruptions
- [ ] Large files
- [ ] Different video formats
- [ ] Permission issues

## 📚 Resources

### Learning Materials
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [M3U8 Format Specification](https://tools.ietf.org/html/rfc8216)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

### Tools
- **Code Editor**: VS Code, PyCharm, or your preference
- **Git GUI**: GitKraken, SourceTree, or command line
- **Testing**: pytest for unit tests
- **Formatting**: Black for code formatting

## 🤝 Community Guidelines

### Be Respectful
- Use welcoming and inclusive language
- Respect different viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Be Collaborative
- Help newcomers get started
- Share knowledge and resources
- Provide constructive feedback
- Celebrate contributions from others

### Communication Channels
- **Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Pull Requests**: Code review and collaboration

## 🏆 Recognition

Contributors are recognized in:
- **README.md**: Major contributors
- **Release Notes**: Feature contributions
- **GitHub**: Automatic contributor tracking

## ❓ Questions?

Need help? Don't hesitate to ask!

- **General Questions**: Open a [Discussion](../discussions)
- **Bug Reports**: Create an [Issue](../issues)
- **Feature Ideas**: Start with a [Discussion](../discussions)

Thank you for contributing! 🙏