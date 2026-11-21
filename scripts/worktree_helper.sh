#!/usr/bin/env bash
# ==============================================================================
# worktree_helper.sh
# Manages ephemeral Git worktrees for Wayne Custom Swarm concurrent builders.
# ==============================================================================

set -euo pipefail

COMMAND="${1:-help}"
WORKER_ID="${2:-}"
EXTRA_ARG="${3:-}"

ensure_git() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ Error: Current directory is not a Git repository." >&2
    exit 1
  fi
}

ensure_gitignore() {
  if [ -f .gitignore ]; then
    if ! grep -q "^\.worktrees/" .gitignore; then
      echo -e "\n.worktrees/" >> .gitignore
      echo "✔ Added .worktrees/ to .gitignore"
    fi
  else
    echo ".worktrees/" > .gitignore
    echo "✔ Created .gitignore with .worktrees/"
  fi
}

case "$COMMAND" in
  add)
    ensure_git
    ensure_gitignore
    if [ -z "$WORKER_ID" ]; then
      echo "Usage: $(basename "$0") add <worker_id> [base_branch]" >&2
      exit 1
    fi
    BASE_BRANCH="${EXTRA_ARG:-$(git branch --show-current)}"
    WT_DIR=".worktrees/worker-${WORKER_ID}"
    WT_BRANCH="swarm/worker-${WORKER_ID}"

    if [ -d "$WT_DIR" ]; then
      echo "⚠️ Worktree already exists at $WT_DIR"
      exit 0
    fi

    # Check if branch exists
    if git show-ref --verify --quiet "refs/heads/$WT_BRANCH"; then
      git worktree add "$WT_DIR" "$WT_BRANCH"
    else
      git worktree add -b "$WT_BRANCH" "$WT_DIR" "$BASE_BRANCH"
    fi
    echo "✅ Provisioned worktree for worker-${WORKER_ID} at $WT_DIR on branch $WT_BRANCH"
    ;;

  sync)
    ensure_git
    if [ -z "$WORKER_ID" ]; then
      echo "Usage: $(basename "$0") sync <worker_id> [target_branch]" >&2
      exit 1
    fi
    TARGET_BRANCH="${EXTRA_ARG:-main}"
    WT_DIR=".worktrees/worker-${WORKER_ID}"

    if [ ! -d "$WT_DIR" ]; then
      echo "❌ Error: Worktree $WT_DIR does not exist." >&2
      exit 1
    fi

    echo "🔄 Re-syncing worker-${WORKER_ID} with $TARGET_BRANCH..."
    git -C "$WT_DIR" merge --ff-only "$TARGET_BRANCH" 2>/dev/null || git -C "$WT_DIR" rebase "$TARGET_BRANCH"
    echo "✅ Worker-${WORKER_ID} successfully re-synchronized with $TARGET_BRANCH"
    ;;

  merge)
    ensure_git
    if [ -z "$WORKER_ID" ]; then
      echo "Usage: $(basename "$0") merge <worker_id> [target_branch]" >&2
      exit 1
    fi
    TARGET_BRANCH="${EXTRA_ARG:-$(git branch --show-current)}"
    WT_BRANCH="swarm/worker-${WORKER_ID}"

    echo "🔀 Merging $WT_BRANCH into $TARGET_BRANCH..."
    git checkout "$TARGET_BRANCH"
    git merge --no-ff "$WT_BRANCH" -m "feat(swarm): integrate changes from worker-${WORKER_ID}"
    echo "✅ Merged $WT_BRANCH into $TARGET_BRANCH"
    ;;

  remove)
    ensure_git
    if [ -z "$WORKER_ID" ]; then
      echo "Usage: $(basename "$0") remove <worker_id>" >&2
      exit 1
    fi
    WT_DIR=".worktrees/worker-${WORKER_ID}"
    WT_BRANCH="swarm/worker-${WORKER_ID}"

    if [ -d "$WT_DIR" ]; then
      git worktree remove --force "$WT_DIR"
      echo "🧹 Removed worktree $WT_DIR"
    fi

    if git show-ref --verify --quiet "refs/heads/$WT_BRANCH"; then
      git branch -D "$WT_BRANCH" 2>/dev/null || true
      echo "🧹 Pruned branch $WT_BRANCH"
    fi
    echo "✅ Cleaned up worker-${WORKER_ID}"
    ;;

  list)
    ensure_git
    git worktree list
    ;;

  help|*)
    cat << USAGE
Usage: $(basename "$0") <command> [args]

Commands:
  add <worker_id> [base_branch]   Provision an isolated worktree in .worktrees/worker-<id>
  sync <worker_id> [target_branch] Re-sync worktree branch with target branch
  merge <worker_id> [target_branch] Merge worker branch into target branch
  remove <worker_id>              Remove worktree and prune branch
  list                            List active Git worktrees
USAGE
    ;;
esac
