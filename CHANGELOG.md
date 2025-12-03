# Changelog

All notable changes to the Task Manager App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2025-12-04

### Added
- Changed README.md to reflect latest version and update author info.

## [0.1.4] - 2025-11-18

### Added
- Added detailed documentation on project structure, developer experience, and core dependencies in `README.md`.
- Changed structure, moved all source files into `src/` directory for better organization.

### Documentation
- 📖 **README.md:** Complete README with badges and quick start
<!-- - 📐 **docs/IDEA.md:** Architecture documentation with diagrams -->
- 🛠️ **QUICKSTART.md:** Setup guide with troubleshooting
- 📝 **CHANGELOG.md:** Changelog for version tracking

### Developer Experience
- `Python`:
  - Modular code structure for scraper, AI processing, and data export
  - Environment variable management with `python-dotenv`
  - Logging and error handling for robustness
<!-- - `GenAI`:
  - Integration with Gemini 2.5 Flash for NLP tasks `google-generativeai` package
  - API Keys stored either as system environment variables or in `.env` file
    - `GEMINI_API_KEY`
  - Prompt engineering for table extraction and sentiment analysis
- `GitHub`:
  - Repository with version control and issue tracking
  - Contribution guidelines in `docs/DEVELOPMENT.md` -->

### Core Cross-Package Dependencies

- `proxy_server`: For custom IP masking and proxy functionality
- `requests`: For HTTP requests to fetch web content
- `beautifulsoup4`: For HTML parsing and data extraction
- `flask`: For building the web interface and API
- `python-dotenv`: For environment variable management
- `urllib3`: For advanced HTTP handling
- `threading`: For concurrent processing

---

## [0.1.3] - 2025-11

### Changed
- Changed documentation 
- Fixed GitHub setup instructions

### Fixed
- Made logging setup use safe defaults if parts of the logging config are omitted
- Merged provided config with defaults so missing keys like logging.format never break things

---

## [0.1.2] - 2025-10

### Added
- Initial public release

---

## [0.1.1] - 2025-09

### Added
- Initial implementation

---

## Future Enhancements

### Planned for v0.1.5
- [ ] Improved error handling and logging
- [ ] Enhanced prompt engineering for better data extraction accuracy
- [ ] Unit tests for core modules
- [ ] Developer documentation enhancements for easier onboarding and contribution

### Planned for v0.2.0
- [ ] PostgreSQL integration for structured data storage
- [ ] Advanced financial analysis metrics
- [ ] Docker containerization for easier deployment
- [ ] UI/UX implementation (desktop app)
- [ ] Power tools for bulk task management
- [ ] Report generation (PDF/Excel)

---
<!-- 
## Contributing

See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for contribution guidelines. -->

## License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.
