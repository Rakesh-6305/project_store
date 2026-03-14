#!/usr/bin/env python3
"""Push project to GitHub repository using Dulwich"""

import os
import time
from pathlib import Path
from dulwich.repo import Repo as DulwichRepo
from dulwich.objects import Blob, Tree, Commit
from dulwich.porcelain import push
from dulwich.client import GitClient, SSHGitClient
import socket
import getpass
from urllib.parse import urlparse

def push_to_github():
    project_dir = r"c:\Users\dwara\OneDrive\Desktop\project_store"
    repo_url = "https://github.com/Rakesh-6305/project_store.git"
    
    print("=" * 50)
    print("StudentProjectHub - GitHub Sync Assistant")
    print("=" * 50)
    print()
    
    try:
        # Initialize Dulwich repository
        print("Initializing Git repository using Dulwich...")
        try:
            repo = DulwichRepo(project_dir)
        except Exception:
            repo = DulwichRepo.init(project_dir)
        
        print("✓ Git repository ready")
        print()
        
        # Stage all files
        print("Staging files...")
        staged_files = []
        for root, dirs, files in os.walk(project_dir):
            # Skip .git directory
            dirs[:] = [d for d in dirs if d != '.git']
            
            for file in files:
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, project_dir)
                
                with open(filepath, 'rb') as f:
                    file_content = f.read()
                
                blob = Blob.from_string(file_content)
                repo.object_store.add_object(blob)
                
                staged_files.append((relpath.replace('\\', '/'), blob.id))
        
        print(f"✓ Staged {len(staged_files)} files")
        print()
        
        # Create tree from staged files
        print("Creating commit tree...")
        tree = Tree()
        for path, blob_id in staged_files:
            tree.add(path.encode(), 0o100644, blob_id)
        
        repo.object_store.add_object(tree)
        
        # Create commit
        print("Creating commit...")
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
        
        print("✓ Commit created")
        print()
        
        # Add remote and push
        print("Adding remote origin...")
        config = repo.get_config()
        config.set((b'remote', b'origin'), b'url', repo_url.encode())
        config.write_to_path()
        print(f"✓ Remote added: {repo_url}")
        print()
        
        print("Pushing to GitHub...")
        try:
            # Try with credentials
            print("\nPlease provide GitHub credentials:")
            print("- For HTTPS: Use your username or Personal Access Token")
            print("- For SSH: Leave empty (if SSH keys are configured)")
            print()
            
            username = input("GitHub username/token (or press Enter for SSH): ").strip()
            
            if username:
                password = getpass.getpass("Password/Token: ").strip()
                push(repo, repo_url, b'refs/heads/main:refs/heads/main',
                     username=username, password=password)
            else:
                # Try SSH
                try:
                    push(repo, repo_url, b'refs/heads/main:refs/heads/main')
                except Exception as e:
                    # If SSH fails, ask for credentials
                    username = input("SSH failed. GitHub username: ").strip()
                    password = getpass.getpass("GitHub Personal Access Token: ").strip()
                    push(repo, repo_url, b'refs/heads/main:refs/heads/main',
                         username=username, password=password)
            
            print("✓ Push successful!")
            print()
            print("Your project has been pushed to:")
            print(repo_url)
        
        except socket.error as e:
            print(f"⚠ Network error: {e}")
            print()
            print("Troubleshooting:")
            print("1. Check your internet connection")
            print("2. Verify firewall settings")
            print("3. Try again with correct credentials")
        except Exception as e:
            print(f"✗ Push failed: {e}")
            print()
            print("To authenticate with GitHub, use one of these methods:")
            print()
            print("METHOD 1: Personal Access Token (Recommended for HTTPS)")
            print("  1. Go to https://github.com/settings/tokens")
            print("  2. Create a new token with 'repo' scope")
            print("  3. Use it as password when prompted")
            print()
            print("METHOD 2: SSH Keys")
            print("  1. Generate SSH key: ssh-keygen -t ed25519 -C 'your-email@example.com'")
            print("  2. Add to GitHub: https://github.com/settings/keys")
            print("  3. Try pushing again (use SSH URL)")
            print()
            print("METHOD 3: GitHub CLI")
            print("  1. Install: https://cli.github.com/")
            print("  2. Authenticate: gh auth login")
            print("  3. Or use this script again")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    push_to_github()
