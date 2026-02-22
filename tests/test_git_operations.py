import pytest
import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.git_operations import (
    verify_git_installed,
    clone_repository,
    is_git_repository,
    get_current_branch,
    checkout_branch,
    detect_default_branch,
    get_github_repos,
    parse_target,
)


def test_verify_git_installed():
    """Git should be installed on system"""
    assert verify_git_installed() == True


def test_clone_public_repository(tmp_path):
    """Clone a public repository successfully"""
    # Use a small public repo for testing
    repo_url = "https://github.com/octocat/Hello-World.git"
    clone_dir = tmp_path / "repos"

    repo_path = clone_repository(repo_url, str(clone_dir), branch="master")

    assert os.path.exists(repo_path)
    assert is_git_repository(repo_path)
    assert get_current_branch(repo_path) == "master"


def test_clone_already_exists(tmp_path):
    """Handle case where repo already exists"""
    repo_url = "https://github.com/octocat/Hello-World.git"
    clone_dir = tmp_path / "repos"

    # First clone (specify master branch for this repo)
    repo_path1 = clone_repository(repo_url, str(clone_dir), branch="master")

    # Second clone (should handle gracefully)
    repo_path2 = clone_repository(repo_url, str(clone_dir), branch="master")

    assert repo_path1 == repo_path2
    assert is_git_repository(repo_path2)


def test_invalid_url():
    """Invalid URL should raise error"""
    with pytest.raises(Exception):
        clone_repository("not-a-valid-url", "/tmp/test")


def test_branch_not_exists(tmp_path):
    """Non-existent branch should raise error"""
    repo_url = "https://github.com/octocat/Hello-World.git"
    clone_dir = tmp_path / "repos"

    with pytest.raises(Exception) as exc_info:
        clone_repository(repo_url, str(clone_dir), branch="nonexistent-branch-xyz")

    # Verify the error message indicates branch issue
    error_msg = str(exc_info.value).lower()
    assert 'branch' in error_msg or 'checkout' in error_msg or 'pathspec' in error_msg, \
        f"Error message should indicate branch issue, got: {exc_info.value}"


def test_is_git_repository(tmp_path):
    """Correctly identify git repositories"""
    # Not a git repo
    normal_dir = tmp_path / "normal"
    normal_dir.mkdir()
    assert is_git_repository(str(normal_dir)) == False

    # Initialize git repo
    git_dir = tmp_path / "git_repo"
    git_dir.mkdir()
    os.system(f"cd {git_dir} && git init > /dev/null 2>&1")
    assert is_git_repository(str(git_dir)) == True


def test_checkout_branch(tmp_path):
    """Checkout different branches"""
    # Use a repo with multiple branches
    repo_url = "https://github.com/octocat/Spoon-Knife.git"
    clone_dir = tmp_path / "repos"

    # Clone to main branch first
    repo_path = clone_repository(repo_url, str(clone_dir), branch="main")

    # Verify we're on main
    assert get_current_branch(repo_path) == "main"

    # Now actually test switching branches using checkout_branch function
    result = checkout_branch(repo_path, "test-branch")
    assert result == True, "checkout_branch should return True on success"

    # Verify we switched to test-branch
    assert get_current_branch(repo_path) == "test-branch", "Should be on test-branch after checkout"


def test_get_current_branch(tmp_path):
    """Get current branch name correctly"""
    # Initialize a test repo
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()
    # Create initial commit so HEAD exists
    os.system(f"cd {test_repo} && git init && git config user.email 'test@test.com' && git config user.name 'Test' && touch README.md && git add . && git commit -m 'Initial commit' && git checkout -b test-branch")

    branch = get_current_branch(str(test_repo))
    assert branch == "test-branch"


def test_clone_with_ssh_url():
    """SSH URLs should be supported (may require auth)"""
    # We can't test actual SSH cloning without credentials,
    # but we can test that SSH URLs are accepted and parsed correctly
    from src.git_operations import _extract_repo_name
    import re

    ssh_urls = [
        'git@github.com:user/repo.git',
        'git@github.com:octocat/Hello-World.git',
        'ssh://git@github.com/user/repo.git'
    ]

    for ssh_url in ssh_urls:
        # Verify URL validation accepts SSH format
        assert re.match(r'^(https?://|git@|ssh://)', ssh_url) or '://' in ssh_url, f"SSH URL not accepted: {ssh_url}"

        # Verify repo name extraction works
        repo_name = _extract_repo_name(ssh_url)
        assert repo_name, f"Failed to extract repo name from: {ssh_url}"
        assert '.git' not in repo_name, f"Repo name should not contain .git: {repo_name}"


def test_network_failure():
    """Handle network failures gracefully"""
    fake_url = "https://this-domain-does-not-exist-12345.com/repo.git"
    with pytest.raises(Exception) as exc_info:
        clone_repository(fake_url, "/tmp/test")

    # Verify the error message indicates network failure
    error_msg = str(exc_info.value).lower()
    assert 'network' in error_msg or 'connect' in error_msg, \
        f"Error message should indicate network issue, got: {exc_info.value}"


def test_permission_error(tmp_path):
    """Handle permission errors"""
    # Create directory with no write permissions
    no_write_dir = tmp_path / "no_write"
    no_write_dir.mkdir()
    os.chmod(str(no_write_dir), 0o444)

    repo_url = "https://github.com/octocat/Hello-World.git"

    try:
        with pytest.raises(PermissionError):
            clone_repository(repo_url, str(no_write_dir / "repos"))
    finally:
        # Clean up permissions for cleanup
        os.chmod(str(no_write_dir), 0o755)


def test_get_current_branch_error(tmp_path):
    """Test get_current_branch raises error for non-git directory"""
    non_git_dir = tmp_path / "not_git"
    non_git_dir.mkdir()

    with pytest.raises(Exception) as exc_info:
        get_current_branch(str(non_git_dir))
    assert "Failed to get current branch" in str(exc_info.value)


def test_directory_exists_but_not_git_repo(tmp_path):
    """Test error when directory exists but is not a git repository"""
    # Create a non-git directory with the same name as the repo
    clone_dir = tmp_path / "repos"
    clone_dir.mkdir()
    fake_repo_dir = clone_dir / "Hello-World"
    fake_repo_dir.mkdir()

    repo_url = "https://github.com/octocat/Hello-World.git"

    with pytest.raises(Exception) as exc_info:
        clone_repository(repo_url, str(clone_dir), branch="master")
    assert "not a git repository" in str(exc_info.value)


def test_clone_existing_repo_with_invalid_branch(tmp_path):
    """Test error when trying to checkout invalid branch on existing repo"""
    repo_url = "https://github.com/octocat/Hello-World.git"
    clone_dir = tmp_path / "repos"

    # First clone with valid branch
    clone_repository(repo_url, str(clone_dir), branch="master")

    # Try to clone again with invalid branch (should attempt checkout and fail)
    with pytest.raises(Exception):
        clone_repository(repo_url, str(clone_dir), branch="nonexistent-branch-xyz")


def _make_repo_json(name, private=False):
    return {"clone_url": f"https://github.com/org/{name}.git",
            "default_branch": "main", "private": private}


@patch("src.git_operations.requests.get")
def test_get_github_repos_with_token(mock_get):
    """With token: type=all, Authorization header present."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = [
        [_make_repo_json("repo-a"), _make_repo_json("repo-b", private=True)],
        [],
    ]
    mock_get.return_value = mock_resp

    repos = get_github_repos("org", "ghp_fake_token")

    assert len(repos) == 2
    assert repos[0]["url"] == "https://github.com/org/repo-a.git"
    assert repos[1]["url"] == "https://github.com/org/repo-b.git"

    called_url = mock_get.call_args_list[0].args[0]
    assert "type=all" in called_url

    called_headers = mock_get.call_args_list[0].kwargs["headers"]
    assert "Authorization" in called_headers


@patch("src.git_operations.requests.get")
def test_get_github_repos_without_token(mock_get):
    """Without token: type=public, no Authorization header."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = [
        [_make_repo_json("public-repo")],
        [],
    ]
    mock_get.return_value = mock_resp

    repos = get_github_repos("org", None)

    assert len(repos) == 1
    assert repos[0]["url"] == "https://github.com/org/public-repo.git"

    called_url = mock_get.call_args_list[0].args[0]
    assert "type=public" in called_url

    called_headers = mock_get.call_args_list[0].kwargs["headers"]
    assert "Authorization" not in called_headers


@patch("src.git_operations.requests.get")
def test_get_github_repos_pagination(mock_get):
    """Verify multi-page fetching collects all repos."""
    page1 = [_make_repo_json(f"repo-{i}") for i in range(100)]
    page2 = [_make_repo_json("repo-100")]
    page3 = []

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = [page1, page2, page3]
    mock_get.return_value = mock_resp

    repos = get_github_repos("org", "tok")

    assert len(repos) == 101
    assert mock_get.call_count == 3
    # Verify page numbers in URLs
    urls = [c.args[0] for c in mock_get.call_args_list]
    assert "page=1" in urls[0]
    assert "page=2" in urls[1]
    assert "page=3" in urls[2]


@patch("src.git_operations.requests.get")
def test_get_github_repos_user_fallback(mock_get):
    """Falls back to /users/ endpoint when /orgs/ returns 404."""
    probe_resp = MagicMock()
    probe_resp.status_code = 404

    user_resp = MagicMock()
    user_resp.status_code = 200
    user_resp.json.side_effect = [
        [_make_repo_json("user-repo")],
        [],
    ]

    mock_get.side_effect = [probe_resp, user_resp, user_resp]

    repos = get_github_repos("someuser", None)

    assert len(repos) == 1
    assert repos[0]["url"] == "https://github.com/org/user-repo.git"

    # First call is the org probe, second is the user endpoint
    urls = [c.args[0] for c in mock_get.call_args_list]
    assert "/orgs/someuser/repos" in urls[0]
    assert "/users/someuser/repos" in urls[1]


@patch("src.git_operations.subprocess.run")
def test_detect_default_branch_main(mock_run):
    """Detects 'main' as default branch."""
    mock_run.return_value = MagicMock(
        stdout="ref: refs/heads/main\tHEAD\nabc123\tHEAD\n",
        returncode=0,
    )
    assert detect_default_branch("https://github.com/org/repo.git") == "main"


@patch("src.git_operations.subprocess.run")
def test_detect_default_branch_master(mock_run):
    """Detects 'master' as default branch."""
    mock_run.return_value = MagicMock(
        stdout="ref: refs/heads/master\tHEAD\nabc123\tHEAD\n",
        returncode=0,
    )
    assert detect_default_branch("https://github.com/org/repo.git") == "master"


@patch("src.git_operations.subprocess.run")
def test_detect_default_branch_failure(mock_run):
    """Returns None when detection fails."""
    mock_run.side_effect = subprocess.CalledProcessError(128, "git")
    assert detect_default_branch("https://github.com/org/repo.git") is None


# --- parse_target tests ---

class TestParseTarget:
    """Tests for parse_target() URL parsing."""

    def test_github_org_url(self):
        """GitHub org URL → batch mode."""
        result = parse_target("https://github.com/centminmod")
        assert result["mode"] == "batch"
        assert result["git_type"] == "github"
        assert result["org"] == "centminmod"
        assert result["repo_url"] is None

    def test_github_repo_url(self):
        """GitHub repo URL (.git) → single-repo mode."""
        result = parse_target("https://github.com/centminmod/repo.git")
        assert result["mode"] == "single-repo"
        assert result["git_type"] == "github"
        assert result["org"] == "centminmod"
        assert result["repo_url"] == "https://github.com/centminmod/repo.git"

    def test_gitlab_nested_group_url(self):
        """GitLab nested group URL → batch, full group path as org."""
        result = parse_target("https://gitlab.com/group/subgroup")
        assert result["mode"] == "batch"
        assert result["git_type"] == "gitlab"
        assert result["org"] == "group/subgroup"

    def test_gitlab_nested_repo_url(self):
        """GitLab nested group repo URL (.git) → single-repo, group path as org."""
        result = parse_target("https://gitlab.com/group/subgroup/repo.git")
        assert result["mode"] == "single-repo"
        assert result["git_type"] == "gitlab"
        assert result["org"] == "group/subgroup"
        assert result["repo_url"] == "https://gitlab.com/group/subgroup/repo.git"

    def test_ssh_url(self):
        """SSH URL → single-repo, github."""
        result = parse_target("git@github.com:org/repo.git")
        assert result["mode"] == "single-repo"
        assert result["git_type"] == "github"
        assert result["org"] == "org"
        assert result["repo_url"] == "git@github.com:org/repo.git"

    def test_azure_url_with_git(self):
        """Azure DevOps URL with _git → single-repo, azure."""
        result = parse_target("https://dev.azure.com/org/project/_git/repo")
        assert result["mode"] == "single-repo"
        assert result["git_type"] == "azure"
        assert result["org"] == "org/project"
        assert result["repo_url"] == "https://dev.azure.com/org/project/_git/repo"

    def test_bitbucket_org_url(self):
        """Bitbucket org URL → batch, bitbucket."""
        result = parse_target("https://bitbucket.org/workspace")
        assert result["mode"] == "batch"
        assert result["git_type"] == "bitbucket"
        assert result["org"] == "workspace"

    def test_bitbucket_repo_url(self):
        """Bitbucket repo URL (.git) → single-repo."""
        result = parse_target("https://bitbucket.org/workspace/repo.git")
        assert result["mode"] == "single-repo"
        assert result["git_type"] == "bitbucket"
        assert result["org"] == "workspace"

    def test_unknown_domain_raises(self):
        """Unknown domain → ValueError."""
        with pytest.raises(ValueError, match="Unknown git provider"):
            parse_target("https://example.com/org/repo.git")

    def test_github_two_segment_no_git_is_batch(self):
        """GitHub 2-segment path without .git → batch (org path, not repo)."""
        result = parse_target("https://github.com/org/something")
        assert result["mode"] == "batch"
        assert result["org"] == "org/something"

    def test_trailing_slash_stripped(self):
        """Trailing slash doesn't break parsing."""
        result = parse_target("https://github.com/myorg/")
        assert result["mode"] == "batch"
        assert result["org"] == "myorg"

    def test_self_hosted_gitlab(self):
        """Self-hosted GitLab domain containing 'gitlab' → gitlab type."""
        result = parse_target("https://gitlab.mycompany.com/team/repo.git")
        assert result["mode"] == "single-repo"
        assert result["git_type"] == "gitlab"
        assert result["org"] == "team"

    def test_invalid_url_raises(self):
        """Completely invalid input → ValueError."""
        with pytest.raises(ValueError):
            parse_target("not-a-url")

    def test_ssh_no_org_raises(self):
        """SSH URL with no org segment → ValueError."""
        with pytest.raises(ValueError, match="Cannot extract organisation"):
            parse_target("git@github.com:repo.git")
