# AI Code Review GitHub Action

An intelligent GitHub Action that performs automated code reviews using Google's Gemini API and CrewAI agents. This action provides comprehensive code analysis including security vulnerabilities, performance issues, code quality assessment, and documentation review.

## ✨ Features

- **🤖 Multi-Agent Analysis**: Uses specialized AI agents for different aspects of code review
- **🔒 Security Analysis**: Identifies vulnerabilities and security best practices
- **⚡ Performance Review**: Analyzes algorithmic complexity and optimization opportunities  
- **📝 Documentation Review**: Assesses code documentation quality and completeness
- **🎯 Smart Filtering**: Configurable file filtering and review scope
- **💬 Rich Comments**: Detailed PR comments and line-level feedback
- **🔧 Highly Configurable**: Customizable review levels and analysis focus

## 🚀 Quick Start

### 1. Set up API Access

Add your Gemini API key to your repository secrets:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add a new secret named `GEMINI_API_KEY` with your Google AI API key
3. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. Create Workflow

Create `.github/workflows/code-review.yml`:

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  ai-code-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: AI Code Review
        uses: ./.github/actions/code-review
        with:
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### 3. Set up the Code Review Action

You have several options:

**Option A: Copy the entire repository**
```bash
# Clone or copy this repository to your project
git clone https://github.com/your-username/code-review-agent.git
```

**Option B: Use as a published container**
```yaml
# In your workflow, use a published container image
uses: docker://ghcr.io/your-username/code-review-agent:latest
```

**Option C: Build from source in your workflow** (see example below)

## ⚙️ Configuration

### Input Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `gemini_api_key` | Google Gemini API key | ✅ | - |
| `github_token` | GitHub token for API access | ✅ | `${{ github.token }}` |
| `max_files` | Maximum number of files to review | ❌ | `20` |
| `review_level` | Review depth: `basic`, `standard`, `comprehensive` | ❌ | `standard` |
| `exclude_patterns` | Comma-separated patterns to exclude | ❌ | `*.lock,*.min.js,*.bundle.js,node_modules/**` |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_SECURITY_ANALYSIS` | Enable security vulnerability analysis | `true` |
| `ENABLE_PERFORMANCE_ANALYSIS` | Enable performance optimization analysis | `true` |
| `ENABLE_DOCUMENTATION_REVIEW` | Enable documentation quality review | `true` |
| `ENABLE_LINE_COMMENTS` | Post line-level comments | `true` |
| `ENABLE_PR_SUMMARY` | Post PR summary comment | `true` |
| `MAX_FILE_SIZE_KB` | Maximum file size to review (KB) | `500` |
| `TIMEOUT_SECONDS` | Analysis timeout per file | `300` |

### Review Levels

- **`basic`**: Code quality and critical issues only
- **`standard`**: Includes security and performance analysis
- **`comprehensive`**: Full analysis including documentation review

## 📋 Example Configurations

### Comprehensive Review
```yaml
- name: Build and Run Comprehensive AI Code Review
  run: |
    docker build -f Containerfile -t code-review-action .
    docker run --rm \
      -e GEMINI_API_KEY="${{ secrets.GEMINI_API_KEY }}" \
      -e GITHUB_TOKEN="${{ secrets.GITHUB_TOKEN }}" \
      -e GITHUB_REPOSITORY="${{ github.repository }}" \
      -e GITHUB_EVENT_PATH="/github/workflow/event.json" \
      -e GITHUB_SHA="${{ github.sha }}" \
      -e GITHUB_REF="${{ github.ref }}" \
      -e REVIEW_LEVEL="comprehensive" \
      -e MAX_FILES="30" \
      -v "${{ github.event_path }}:/github/workflow/event.json" \
      -v "${{ github.workspace }}:/github/workspace" \
      -w /github/workspace \
      code-review-action
```

### Security-Focused Review
```yaml
- name: Security-Focused Review
  run: |
    docker build -f Containerfile -t code-review-action .
    docker run --rm \
      -e GEMINI_API_KEY="${{ secrets.GEMINI_API_KEY }}" \
      -e GITHUB_TOKEN="${{ secrets.GITHUB_TOKEN }}" \
      -e GITHUB_REPOSITORY="${{ github.repository }}" \
      -e GITHUB_EVENT_PATH="/github/workflow/event.json" \
      -e GITHUB_SHA="${{ github.sha }}" \
      -e GITHUB_REF="${{ github.ref }}" \
      -e REVIEW_LEVEL="standard" \
      -e ENABLE_PERFORMANCE_ANALYSIS="false" \
      -e ENABLE_DOCUMENTATION_REVIEW="false" \
      -v "${{ github.event_path }}:/github/workflow/event.json" \
      -v "${{ github.workspace }}:/github/workspace" \
      -w /github/workspace \
      code-review-action
```

### Using Published Container
```yaml
- name: AI Code Review
  uses: docker://ghcr.io/your-username/code-review-agent:latest
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_REPOSITORY: ${{ github.repository }}
    GITHUB_EVENT_PATH: ${{ github.event_path }}
    GITHUB_SHA: ${{ github.sha }}
    GITHUB_REF: ${{ github.ref }}
    MAX_FILES: "50"
    MAX_FILE_SIZE_KB: "1000"
```

## 🔍 Supported File Types

### Programming Languages
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.ts`, `.jsx`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`)
- C# (`.cs`)
- PHP (`.php`)
- Ruby (`.rb`)
- Go (`.go`)
- Rust (`.rs`)
- Swift (`.swift`)
- Kotlin (`.kt`)
- Scala (`.scala`)
- SQL (`.sql`)
- R (`.r`, `.R`)
- Perl (`.pl`, `.pm`)
- Lua (`.lua`)
- Clojure (`.clj`, `.cljs`)
- Elixir (`.ex`, `.exs`)
- MATLAB (`.m`)
- And more...

### Configuration & Documentation
- YAML/JSON (`.yml`, `.yaml`, `.json`)
- TOML (`.toml`)
- XML (`.xml`)
- HTML/CSS (`.html`, `.css`, `.scss`, `.sass`, `.less`)
- Markdown (`.md`)
- reStructuredText (`.rst`)
- Text files (`.txt`)
- Configuration files (`.cfg`, `.ini`, `.conf`, `.properties`)
- Environment files (`.env`)
- Git files (`.gitignore`, `.gitattributes`)

### Scripts & Build Files  
- Shell scripts (`.sh`, `.bash`)
- Windows scripts (`.bat`, `.ps1`)
- Makefiles (`Makefile`)
- Dockerfiles (`Dockerfile`)
- And more special files...

## 📊 Review Output

The action provides:

### PR Summary Comment
- Overall code quality metrics
- Critical issues summary  
- Security analysis results
- Performance optimization opportunities
- Documentation quality assessment
- Prioritized recommendations

### Line Comments
- Specific issue descriptions
- Suggested fixes with examples
- Security vulnerability details
- Performance improvement suggestions

### GitHub Action Outputs
- `review_summary`: Brief review summary
- `issues_found`: Total number of issues
- `recommendations`: Key recommendations

## 🛠️ Advanced Usage

### Custom Agent Configuration

Create a `.code-review-config.yml` in your repository root:

```yaml
agents:
  security_analyst:
    enabled: true
    focus_areas: ["owasp", "vulnerabilities", "secure_coding"]
  performance_analyst:
    enabled: true
    focus_areas: ["complexity", "memory", "optimization"]
  documentation_reviewer:
    enabled: true
    focus_areas: ["docstrings", "comments", "api_docs"]

output:
  max_comment_length: 500
  include_examples: true
  severity_threshold: "medium"
```

### Integration with Other Actions

```yaml
jobs:
  ai-code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      # Run tests first
      - name: Run Tests
        run: npm test
        
      # Then run AI review
      - name: AI Code Review
        uses: ./.github/actions/code-review
        with:
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          
      # Optional: Block merge if critical issues found
      - name: Check Review Results
        if: steps.ai-review.outputs.issues_found > 10
        run: |
          echo "Too many issues found: ${{ steps.ai-review.outputs.issues_found }}"
          exit 1
```

## 🔧 Development

### Local Testing

#### Method 1: Test with Existing Git Repository (Recommended)

This method uses an existing git repository with real commits for the most realistic testing.

1. **Build the container:**
   ```bash
   podman build -t localhost/code-review-action:latest .
   # Or with Docker: docker build -t localhost/code-review-action:latest .
   ```

2. **Get real commit SHAs from your repository:**
   ```bash
   cd /path/to/your/git/repository
   git log --oneline -5  # Get recent commit SHAs
   ```

3. **Create GitHub event file with real commit SHAs:**
   ```bash
   # Replace HEAD_SHA and BASE_SHA with actual commits from your repo
   cat > event.json << 'EOF'
   {
     "action": "opened",
     "number": 1,
     "pull_request": {
       "head": {"sha": "HEAD_SHA"},
       "base": {"sha": "BASE_SHA"}
     }
   }
   EOF
   ```

4. **Run the container:**
   ```bash
   podman run --rm \
     -e GEMINI_API_KEY="your-gemini-api-key" \
     -e GITHUB_TOKEN="ghp_dummy_token_for_local_testing" \
     -e GITHUB_REPOSITORY="owner/repo-name" \
     -e GITHUB_EVENT_PATH="/github/event.json" \
     -e GITHUB_SHA="HEAD_SHA" \
     -e GITHUB_REF="refs/pull/1/merge" \
     -e MAX_FILES="10" \
     -e REVIEW_LEVEL="standard" \
     -e ENABLE_LINE_COMMENTS="false" \
     -e ENABLE_PR_SUMMARY="false" \
     -v "/path/to/your/git/repository":/github/workspace \
     -v "$(pwd)/event.json":/github/event.json \
     -w /github/workspace \
     localhost/code-review-action:latest
   ```

#### Method 2: Python Environment Testing
1. Clone the repository
2. Create virtual environment:
   ```bash
   python3 -m venv test_env
   source test_env/bin/activate  # On Windows: test_env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   export GITHUB_TOKEN="your-token"
   export GITHUB_REPOSITORY="owner/repo"
   ```
5. Run directly:
   ```bash
   cd src && python main.py
   ```

#### Method 3: Quick Test with Temporary Repository

1. **Create a test repository:**
   ```bash
   mkdir -p /tmp/test-repo
   cd /tmp/test-repo
   git init
   echo "def hello(): print('Hello, World!')" > test.py
   git add test.py
   git commit -m "Initial commit"
   
   echo "def hello(): print('Hello, Universe!')" > test.py
   git add test.py
   git commit -m "Update greeting"
   ```

2. **Get commit SHAs:**
   ```bash
   LATEST_SHA=$(git rev-parse HEAD)
   PREVIOUS_SHA=$(git rev-parse HEAD~1)
   echo "Latest: $LATEST_SHA, Previous: $PREVIOUS_SHA"
   ```

3. **Create event file:**
   ```bash
   cat > /tmp/event.json << EOF
   {
     "action": "opened",
     "number": 1,
     "pull_request": {
       "head": {"sha": "$LATEST_SHA"},
       "base": {"sha": "$PREVIOUS_SHA"}
     }
   }
   EOF
   ```

4. **Run container:**
   ```bash
   podman run --rm \
     -e GEMINI_API_KEY="your-gemini-api-key" \
     -e GITHUB_TOKEN="dummy-token" \
     -e GITHUB_REPOSITORY="test/repo" \
     -e GITHUB_EVENT_PATH="/github/event.json" \
     -e GITHUB_SHA="$LATEST_SHA" \
     -e GITHUB_REF="refs/pull/1/merge" \
     -e MAX_FILES="5" \
     -e REVIEW_LEVEL="basic" \
     -e ENABLE_LINE_COMMENTS="false" \
     -e ENABLE_PR_SUMMARY="false" \
     -v /tmp/test-repo:/github/workspace \
     -v /tmp/event.json:/github/event.json \
     -w /github/workspace \
     localhost/code-review-action:latest
   ```

#### Method 4: Test Specific GitHub Pull Request

1. **Use existing PR from a real repository:**
   ```bash
   # Clone the repository with the PR you want to test
   git clone https://github.com/owner/repo.git
   cd repo
   
   # Check out the PR branch (optional, or use remote commits)
   git fetch origin pull/PR_NUMBER/head:pr-branch
   git checkout pr-branch
   
   # Get the actual commit SHAs from the PR
   BASE_SHA="actual-base-commit-sha"
   HEAD_SHA="actual-head-commit-sha"
   ```

2. **Create event file with real PR data:**
   ```bash
   cat > event.json << EOF
   {
     "action": "opened",
     "number": PR_NUMBER,
     "pull_request": {
       "head": {"sha": "$HEAD_SHA"},
       "base": {"sha": "$BASE_SHA"}
     }
   }
   EOF
   ```

3. **Run with real repository:**
   ```bash
   podman run --rm \
     -e GEMINI_API_KEY="your-gemini-api-key" \
     -e GITHUB_TOKEN="your-github-token" \
     -e GITHUB_REPOSITORY="owner/repo" \
     -e GITHUB_EVENT_PATH="/github/event.json" \
     -e GITHUB_SHA="$HEAD_SHA" \
     -e GITHUB_REF="refs/pull/PR_NUMBER/merge" \
     -e MAX_FILES="20" \
     -e REVIEW_LEVEL="comprehensive" \
     -e ENABLE_LINE_COMMENTS="false" \
     -e ENABLE_PR_SUMMARY="false" \
     -v "$(pwd)":/github/workspace \
     -v "$(pwd)/event.json":/github/event.json \
     -w /github/workspace \
     localhost/code-review-action:latest
   ```

#### Required Files Checklist

Before running, ensure you have:

- ✅ **event.json**: GitHub event payload with PR information
- ✅ **Git repository**: Directory with .git folder and commit history  
- ✅ **Valid commit SHAs**: Real commits that exist in the repository
- ✅ **Gemini API key**: Valid Google AI API key
- ✅ **Built container**: Successfully built container image
- ✅ **File permissions**: Read access to the repository directory

#### Troubleshooting Common Issues

**"fatal: ambiguous argument 'base123...head456'"**
- Use real commit SHAs from your repository instead of dummy values

**"No such file or directory"**  
- Ensure the event.json file exists and is properly mounted
- Check that the repository path is correct and accessible

**"No files to review"**
- Verify there are actual changes between the base and head commits
- Check that file types are supported (see supported extensions)

**"Failed to initialize Gemini client"**
- Verify your GEMINI_API_KEY is valid and properly set
- Check your API quota and permissions

#### Method 3: Component Testing
Test individual components without full GitHub simulation:
```bash
# Test Gemini client only
python3 -c "
import sys
sys.path.insert(0, '.github/actions/code-review/src')
from tools.gemini_client import GeminiClient

client = GeminiClient('your-api-key')
result = client.analyze_code('def hello(): pass', 'test.py')
print('✅ Gemini client working:', result.get('summary', 'No summary'))
"
```

### Building and Testing the Container

```bash
# Build the container
cd .github/actions/code-review
podman build -f Containerfile -t code-review-action:latest .

# Quick test (should show help/error about missing environment)
podman run --rm code-review-action:latest

# Full test with your API key
podman run --rm \
  -e GEMINI_API_KEY="your-key" \
  -e GITHUB_REPOSITORY="test/repo" \
  -e ENABLE_LINE_COMMENTS="false" \
  code-review-action:latest
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Join discussions in GitHub Discussions
- **Documentation**: Check the docs/ directory for detailed guides

## 🙏 Acknowledgments

- Google Gemini API for AI-powered analysis
- CrewAI framework for multi-agent coordination
- GitHub Actions platform for CI/CD integration

---

**Note**: This action sends code to Google's Gemini API for analysis. Ensure this complies with your organization's security policies for sensitive codebases.