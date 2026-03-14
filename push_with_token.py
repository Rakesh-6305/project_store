#!/usr/bin/env python3
"""
Push project to GitHub repository using Dulwich
This version auto-completes without prompting for credentials
"""

import os
import sys
import time
from pathlib import Path
from dulwich.repo import Repo as DulwichRepo
from dulwich.objects import Blob, Tree, Commit
from dulwich.porcelain import push
import base64

def push_to_github(token=None):
    project_dir = r"c:\Users\dwara\OneDrive\Desktop\project_store"
    repo_url = "https://github.com/Rakesh-6305/project_store.git"
    
    print("=" * 60)
    print("StudentProjectHub - GitHub Sync Assistant (Auto-Mode)")
    print("=" * 60)
    print()
    
    try:
        # Initialize Dulwich repository
        print("[1/6] Initializing Git repository...")
        try:
            repo = DulwichRepo(project_dir)
        except Exception:
            repo = DulwichRepo.init(project_dir)
        
        print("      ✓ Git repository ready")
        print()
        
        # Stage all files
        print("[2/6] Staging files...")
        staged_files = []
        for root, dirs, files in os.walk(project_dir):
            # Skip .git directory and __pycache__
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__']]
            
            for file in files:
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, project_dir)
                
                try:
                    with open(filepath, 'rb') as f:
                        file_content = f.read()
                    
                    blob = Blob.from_string(file_content)
                    repo.object_store.add_object(blob)
                    
                    staged_files.append((relpath.replace('\\', '/'), blob.id))
                except Exception as e:
                    print(f"      ⚠ Skipping {relpath}: {e}")
        
        print(f"      ✓ Staged {len(staged_files)} files")
        print()
        
        # Create tree from staged files
        print("[3/6] Creating commit tree...")
        tree = Tree()
        for path, blob_id in staged_files:
            tree.add(path.encode(), 0o100644, blob_id)
        
        repo.object_store.add_object(tree)
        print("      ✓ Tree created")
        print()
        
        # Create commit
        print("[4/6] Creating commit...")
        commit = Commit()
        commit.tree = tree.id
        commit.author = commit.committer = b"Project Store <project@store.com>"
        commit.author_time = commit.commit_time = int(time.time())
        commit.author_timezone = commit.commit_timezone = 0
        commit.encoding = b"UTF-8"
        commit.message = b"Final premium Hub with all technical fixes"
        
        repo.object_store.add_object(commit)
        
        # Update reference
        repo.refs[b'refs/heads/main'] = commit.id
        repo.refs.set_symbolic_ref(b'HEAD', b'refs/heads/main')
        
        print("      ✓ Commit created")
        print()
        
        # Add remote
        print("[5/6] Configuring remote...")
        config = repo.get_config()
        config.set((b'remote', b'origin'), b'url', repo_url.encode())
        config.write_to_path()
        print(f"      ✓ Remote: {repo_url}")
        print()
        
        # Push to GitHub
        print("[6/6] Pushing to GitHub...")
        if token:
            try:
                push(repo, repo_url, b'refs/heads/main:refs/heads/main',
                     username=token, password='x-oauth-basic')
                print("      ✓ Push successful!")
            except Exception as e:
                print(f"      ✗ Push failed with token: {e}")
                raise
        else:
            push(repo, repo_url, b'refs/heads/main:refs/heads/main')
            print("      ✓ Push successful!")
        
        print()
        print("=" * 60)
        print("✓ PROJECT SUCCESSFULLY PUSHED TO GITHUB!")
        print()
        print("Repository URL: " + repo_url)
        print("=" * 60)
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print()
        print("=" * 60)
        print("TO COMPLETE THE PUSH:")
        print("=" * 60)
        print()
        print("1. Create a Personal Access Token:")
        print("   - Go to: https://github.com/settings/tokens")
        print("   - Click 'Generate new token (classic)'")
        print("   - Scopes: Select 'repo' (Full control of private repositories)")
        print("   - Copy the generated token")
        print()
        print("2. Run this script with your token:")
        print("   - Create an environment variable: GITHUB_TOKEN=your_token_here")
        print("   - Run the script again")
        print()
        print("   OR")
        print()
        print("3. Edit this script and replace 'token = None' with:")
        print("   token = 'your_personal_access_token'")
        print()
        return False

if __name__ == "__main__":
    # You can set your token here or use environment variable
    token = os.environ.get('GITHUB_TOKEN')
    
    # Fallback: set token directly here if needed
    # token = 'ghp_YOUR_TOKEN_HERE'
    
    success = push_to_github(token)
    sys.exit(0 if success else 1)
