# Changelog

All notable changes to ClaudeBox will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-01-01

### Added
- **Session Persistence**: Persistent sessions with workspace management at `~/.claudebox/sessions/`
  - `session_id` parameter for persistent sessions
  - `ClaudeBox.reconnect()` classmethod to reconnect to existing sessions
  - `ClaudeBox.list_sessions()` classmethod to enumerate all sessions
  - `ClaudeBox.cleanup_session()` classmethod for manual cleanup
- **Structured Logging**: JSON Lines logging to `history.jsonl` for debugging and RL training
  - `ActionLogger` class for structured action logging
  - Session metadata tracking in `session.json`
  - Resource metrics collection
- **Modular Skills System**: 9 built-in skills for extending capabilities
  - `EMAIL_SKILL` - Send emails via SendGrid
  - `POSTGRES_SKILL` - PostgreSQL database connections
  - `MYSQL_SKILL` - MySQL database connections
  - `REDIS_SKILL` - Redis data store
  - `API_SKILL` - HTTP requests with requests/httpx
  - `AWS_SKILL` - AWS SDK (boto3)
  - `DOCKER_SKILL` - Docker CLI
  - `SCRAPING_SKILL` - Web scraping (BeautifulSoup, Playwright)
  - `DATA_SCIENCE_SKILL` - Data science stack (pandas, numpy, matplotlib)
  - Custom skill creation with `Skill` dataclass
  - Skill registry for managing skills
- **Sandbox Templates**: 6 pre-configured environments
  - `SandboxTemplate.DEFAULT` - Base runtime
  - `SandboxTemplate.WEB_DEV` - Web development (Node.js, TypeScript, Docker)
  - `SandboxTemplate.DATA_SCIENCE` - Data science (Jupyter, pandas, scikit-learn)
  - `SandboxTemplate.SECURITY` - Security research (nmap, wireshark) *for authorized use only*
  - `SandboxTemplate.DEVOPS` - DevOps tools (Docker, Kubernetes CLI)
  - `SandboxTemplate.MOBILE` - Mobile development
- **RL Training Support**: Reinforcement learning scaffolding
  - 5 built-in reward functions: `SuccessOnlyReward`, `CodeQualityReward`, `SafetyReward`, `EfficiencyReward`, `CustomReward`
  - `combine_rewards()` to merge multiple reward functions
  - `TrajectoryExporter` for exporting training data
  - State-action pair extraction
  - Trajectory merging for multi-session training
- **Security Policies**: Fine-grained security control
  - 5 pre-defined policies: `UNRESTRICTED`, `STANDARD`, `RESTRICTED`, `READONLY`, `RESEARCH`
  - Custom security policy creation
  - Network access restrictions
  - Filesystem isolation
  - Command blocking
  - Resource limits
  - `SecurityPolicyEnforcer` for policy enforcement
- **Observability**: Enhanced monitoring capabilities
  - `get_metrics()` method for current resource usage
  - `get_history_metrics()` method for historical metrics
  - Structured action logging

### Changed
- Enhanced `ClaudeBox` constructor with new parameters:
  - `session_id` - For persistent sessions
  - `workspace_dir` - Custom workspace location
  - `enable_logging` - Toggle structured logging
  - `skills` - List of skills to pre-load
  - `template` - Sandbox template selection
  - `reward_fn` - Reward function for RL training
  - `security_policy` - Security policy to enforce
- `CodeResult` dataclass now includes:
  - `reward` field - Calculated reward (if reward function provided)
  - `action_log` field - List of actions taken during execution
- Improved error handling and type hints throughout codebase

### Fixed
- Import ordering issues (ruff compliance)
- Type checking errors (mypy compliance)
- File opening modes in trajectory export
- Unused variable warnings

## [0.1.1] - 2024-12-XX

### Added
- Initial PyPI publishing workflow
- Docker image publishing to GHCR

### Changed
- Fixed Docker image name in publish workflow
- Improved import ordering in box.py

### Fixed
- Docker image naming consistency

## [0.1.0] - 2024-12-XX

### Added
- Initial release of ClaudeBox
- Basic `ClaudeBox` class for running Claude Code in micro-VMs
- Integration with BoxLite for hardware isolation
- `code()` method for executing Claude Code commands
- OAuth token authentication support
- Basic error handling and result types
- MIT License

[unreleased]: https://github.com/boxlite-labs/claudebox/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/boxlite-labs/claudebox/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/boxlite-labs/claudebox/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/boxlite-labs/claudebox/releases/tag/v0.1.0
