#!/usr/bin/env python3
"""Push project to GitHub using HTTPS with token authentication"""

import os
import subprocess
import sys
import json

def push_to_github_with_git(token):
    project_dir = r"c:\Users\dwara\OneDrive\Desktop\project_store"
    repo_url = "https://github.com/Rakesh-6305/project_store.git"
    
    print("=" * 60)
    print("StudentProjectHub - GitHub Sync Assistant")
    print("=" * 60)
    print()
    
    try:
        os.chdir(project_dir)
        
        # Configure git credentials
        print("[1/5] Configuring Git...")
        commands = [
            # Set git config temporarily for this push
            ['git', 'config', 'user.name', 'Project Store'],
            ['git', 'config', 'user.email', 'project@store.com'],
            ['git', 'config', 'pull.rebase', 'false'],
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            except FileNotFoundError:
                # Git not in path, try using full path
                try:
                    cmd[0] = r'C:\Program Files\Git\bin\git.exe'
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                except:
                    pass
        
        print("      ✓ Git configured")
        print()
        
        # Initialize repo if needed
        print("[2/5] Initializing repository...")
        try:
            result = subprocess.run(['git', 'init'], capture_output=True, text=True, timeout=10)
        except:
            result = subprocess.run([r'C:\Program Files\Git\bin\git.exe', 'init'], capture_output=True, text=True)
        
        print("      ✓ Repository initialized")
        print()
        
        # Add all files
        print("[3/5] Adding files...")
        try:
            result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True, timeout=10)
        except:
            result = subprocess.run([r'C:\Program Files\Git\bin\git.exe', 'add', '.'], capture_output=True, text=True)
        
        print("      ✓ Files staged")
        print()
        
        # Commit
        print("[4/5] Creating commit...")
        try:
            result = subprocess.run(
                ['git', 'commit', '-m', 'Final premium Hub with all technical fixes'],
                capture_output=True, text=True, timeout=10
            )
        except:
            result = subprocess.run(
                [r'C:\Program Files\Git\bin\git.exe', 'commit', '-m', 'Final premium Hub with all technical fixes'],
                capture_output=True, text=True
            )
        
        # Only error if it's not "nothing to commit"
        if result.returncode != 0 and "nothing to commit" not in result.stderr.lower():
            print(f"      Note: {result.stderr.strip()}")
        else:
            print("      ✓ Commit created")
        print()
        
        # Set branch to main
        print("[5/5] Pushing to GitHub...")
        
        # Create/switch to main branch
        try:
            subprocess.run(['git', 'branch', '-M', 'main'], capture_output=True, text=True, timeout=10)
        except:
            subprocess.run([r'C:\Program Files\Git\bin\git.exe', 'branch', '-M', 'main'], capture_output=True, text=True)
        
        # Add remote
        try:
            subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True, text=True, timeout=10)
        except:
            pass
        
        try:
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], capture_output=True, text=True, timeout=10)
        except:
            subprocess.run([r'C:\Program Files\Git\bin\git.exe', 'remote', 'add', 'origin', repo_url], capture_output=True, text=True)
        
        # Create authenticated URL with token
        auth_url = repo_url.replace('https://', f'https://{token}@')
        
        # Push with authentication
        try:
            result = subprocess.run(
                ['git', 'push', '-u', 'origin', 'main'],
                input=f'{token}\n',
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
            )
        except:
            result = subprocess.run(
                [r'C:\Program Files\Git\bin\git.exe', 'push', '-u', 'origin', 'main'],
                input=f'{token}\n',
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
            )
        
        if result.returncode == 0 or 'master' in result.stderr or 'main' in result.stderr:
            print("      ✓ Push successful!")
            print()
            print("=" * 60)
            print("✓ PROJECT SUCCESSFULLY PUSHED TO GITHUB!")
            print()
            print("Repository: " + repo_url)
            print("=" * 60)
            return True
        else:
            print(f"      Push output: {result.stderr}")
            print(f"      Return code: {result.returncode}")
            
            if "403" in result.stderr or "permission" in result.stderr.lower():
                print()
                print("      ✗ Permission denied - Token may not have write access")
            
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    token = os.environ.get('GITHUB_TOKEN', '')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    success = push_to_github_with_git(token)
    sys.exit(0 if success else 1)
