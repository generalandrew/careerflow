#!/usr/bin/env bash
# careerflow setup script for Mac and Linux
# Creates a workspace folder, copies scripts, installs dependencies, scaffolds templates.

set -euo pipefail

# Default workspace path, override with first arg
WORKSPACE="${1:-$HOME/Documents/careerflow-workspace}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "careerflow setup"
echo "  Repo directory:    $REPO_DIR"
echo "  Workspace target:  $WORKSPACE"
echo ""

# 1. Create workspace
mkdir -p "$WORKSPACE"/{master/source_documents,scripts,docs,skills/onboarding,skills/application,templates/master,applications}

# 2. Copy scripts
echo "Copying scripts..."
cp -R "$REPO_DIR/scripts/." "$WORKSPACE/scripts/"

# 3. Copy docs
echo "Copying docs..."
cp -R "$REPO_DIR/docs/." "$WORKSPACE/docs/"

# 4. Copy skills
echo "Copying skills..."
cp -R "$REPO_DIR/skills/." "$WORKSPACE/skills/"

# 5. Copy templates
echo "Copying templates..."
cp -R "$REPO_DIR/templates/." "$WORKSPACE/templates/"

# 6. Initialize master files from templates if not yet present
for tmpl in "$WORKSPACE/templates/master/"*.template; do
  base=$(basename "$tmpl" .template)
  target="$WORKSPACE/master/$base"
  if [ ! -f "$target" ]; then
    cp "$tmpl" "$target"
    echo "  Initialized $target"
  fi
done

# 7. Initialize applications.xlsx if not present
if [ ! -f "$WORKSPACE/applications.xlsx" ]; then
  echo "Generating empty applications.xlsx..."
  python3 "$WORKSPACE/scripts/init_workspace.py" --xlsx "$WORKSPACE/applications.xlsx"
fi

# 8. Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user openpyxl || pip3 install --break-system-packages openpyxl || true

# 9. Install Node dependencies
echo "Installing Node dependencies..."
if [ ! -d "$WORKSPACE/node_modules/docx" ]; then
  ( cd "$WORKSPACE" && npm init -y >/dev/null && npm install docx --silent )
fi

# 10. Friendly close
echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "  1. Open Claude Code or Cowork mode."
echo "  2. Grant Claude access to: $WORKSPACE"
echo "  3. Tell Claude: 'set up my job search'"
echo ""
echo "Workspace ready at: $WORKSPACE"
