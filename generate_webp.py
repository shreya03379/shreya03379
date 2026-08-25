#!/usr/bin/env python3
"""Generate GitHub Space Shooter WebP for profile.

This script fetches your GitHub contribution data and generates
an animated space shooter WebP that can be displayed on your profile.

Configuration:
    Edit the variables below to customize the output.
"""

import os
import sys

# Get the absolute path to the project root (where src/ folder is located)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Add project root to path so Python can find 'src' as a package
sys.path.insert(0, PROJECT_ROOT)

from src.github_client import GitHubClient
from src.game import Animator, RandomStrategy, ColumnStrategy, RowStrategy

# ============================================================
# CONFIGURATION - Pulled dynamically from environment variables
# ============================================================

USERNAME = os.getenv("GITHUB_OWNER")
if not USERNAME:
    print("=" * 60)
    print("ERROR: GITHUB_OWNER environment variable not set!")
    print("=" * 60)
    sys.exit(1)

OUTPUT_FILE = os.getenv("OUTPUT_FILE", "game.webp")
STRATEGY = os.getenv("ANIMATION_STRATEGY", "random")

# Parse FPS
try:
    FPS = int(os.getenv("ANIMATION_FPS", "40"))
except ValueError:
    print("Warning: ANIMATION_FPS is not a valid integer. Defaulting to 40.")
    FPS = 40

# Parse MAX_FRAMES
env_max_frames = os.getenv("MAX_FRAMES")
if env_max_frames and env_max_frames.strip():
    try:
        MAX_FRAMES = int(env_max_frames)
    except ValueError:
        print("Warning: MAX_FRAMES is not a valid integer. Ignoring.")
        MAX_FRAMES = None
else:
    MAX_FRAMES = None

# ============================================================


def get_strategy(strategy_name: str):
    """Get strategy instance by name."""
    strategies = {
        "random": RandomStrategy,
        "column": ColumnStrategy,
        "row": RowStrategy,
    }
    if strategy_name not in strategies:
        print(f"Error: Unknown strategy '{strategy_name}'")
        print(f"Available strategies: {', '.join(strategies.keys())}")
        sys.exit(1)
    return strategies[strategy_name]()


def main():
    """Main entry point."""
    # Get token from environment
    token = os.getenv("GH_TOKEN")
    if not token:
        print("=" * 60)
        print("ERROR: GH_TOKEN environment variable not set!")
        print("=" * 60)
        print("\nTo run locally, set your GitHub token:")
        print("  Windows:  set GH_TOKEN=your_token_here")
        print("  Linux:    export GH_TOKEN=your_token_here")
        print("\nTo create a token:")
        print("  1. Go to https://github.com/settings/tokens")
        print("  2. Generate new token (classic)")
        print("  3. Select scope: read:user")
        print("=" * 60)
        sys.exit(1)
    
    print(f"🎮 GitHub Space Shooter WebP Generator")
    print(f"=" * 40)
    print(f"Username: {USERNAME}")
    print(f"Strategy: {STRATEGY}")
    print(f"FPS: {FPS}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"=" * 40)
    
    # Fetch contribution data
    print(f"\n📊 Fetching contribution data for {USERNAME}...")
    try:
        with GitHubClient(token) as client:
            data = client.get_contribution_graph(USERNAME)
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        sys.exit(1)
    
    print(f"✓ Found {data['total_contributions']} contributions in the last year")
    
    # Get strategy
    strategy = get_strategy(STRATEGY)
    
    # Generate animation
    print(f"\n🎬 Generating WebP animation...")
    print(f"   This may take a minute...")
    
    try:
        animator = Animator(data, strategy, fps=FPS)
        webp_buffer = animator.generate_webp(maxFrame=MAX_FRAMES)
        
        with open(OUTPUT_FILE, "wb") as f:
            f.write(webp_buffer.getvalue())
        
        file_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)  # MB
        print(f"\n✅ Success!")
        print(f"   WebP saved to: {OUTPUT_FILE}")
        print(f"   File size: {file_size:.2f} MB")
        
    except Exception as e:
        print(f"❌ Error generating WebP: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
