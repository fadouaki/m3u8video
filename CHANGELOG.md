# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced README with comprehensive documentation
- Contributing guidelines
- Proper project licensing (MIT)
- Professional repository structure

## [1.2.0] - 2025-01-XX

### Added
- Cross-platform FFmpeg detection and path resolution
- Smart temporary directory handling for PyInstaller executables
- Thread-safe GUI updates with proper error handling
- FFmpeg availability testing on application startup
- Enhanced error messages with helpful solutions
- Comprehensive logging with progress tracking

### Fixed
- **Critical**: "Read-only file system" error when running PyInstaller executables
- **Critical**: Hardcoded FFmpeg path causing failures on different systems
- GUI freezing during downloads by implementing proper threading
- Memory leaks from improper temporary file cleanup
- Cross-platform compatibility issues

### Changed
- Improved build configuration to reduce antivirus false positives
- Enhanced version information for Windows executables
- Better error handling with user-friendly messages
- Modernized GUI styling and layout

### Security
- Added input validation for M3U8 URLs
- Improved file handling with proper permissions checking
- Secure temporary directory creation

## [1.1.0] - 2024-XX-XX

### Added
- GUI application with Tkinter interface
- Dark theme styling for modern appearance
- Real-time download progress display
- File save dialog integration

### Changed
- Migrated from command-line only to GUI application
- Improved user experience with visual feedback

## [1.0.0] - 2024-XX-XX

### Added
- Initial release
- Command-line M3U8 video downloader (`m3u8vi.py`)
- Support for master and media playlists
- Automatic quality selection (highest resolution)
- FFmpeg integration for video concatenation
- Basic error handling and retry logic
- Cross-platform support (Windows, macOS, Linux)

### Features
- Downloads video segments from M3U8/HLS playlists
- Handles both variant (master) and media playlists
- Automatically selects highest available quality
- Robust error handling with retry mechanisms
- Temporary file management and cleanup
- Progress reporting and logging

---

## Version History Summary

- **v1.2.0**: Production-ready with PyInstaller fixes and enhanced UX
- **v1.1.0**: GUI application with modern interface
- **v1.0.0**: Initial command-line implementation

## Migration Guide

### From v1.1.x to v1.2.x
- No breaking changes for end users
- Developers: Updated build process with new PyInstaller options
- New features automatically available after update

### From v1.0.x to v1.1.x
- Command-line functionality preserved in `m3u8vi.py`
- New GUI application in `app.py`
- Same core functionality with improved user interface

## Known Issues

### Current
- Windows antivirus may flag PyInstaller executables (false positive)
- Large video files may require significant disk space during processing
- Network interruptions require manual restart

### Planned Fixes
- Code signing to reduce antivirus false positives
- Resume capability for interrupted downloads
- Bandwidth throttling options

## Support

For issues, feature requests, or questions:
- GitHub Issues: [Report a bug or request a feature](https://github.com/yourusername/m3u8-downloader/issues)
- Documentation: Check the README.md for detailed usage instructions
- Community: Join discussions for help and tips

---

**Note**: This project follows semantic versioning. Version numbers indicate:
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backwards compatible  
- **Patch** (0.0.X): Bug fixes, backwards compatible