"""
Colab module: Bridge to execute heavy batch tasks / ML workloads
via WSL's Google Colab CLI.
"""

from pathlib import Path
import subprocess
from typing import Dict, List, Optional


class ColabBridge:
    """Invokes Google Colab CLI in WSL for cloud GPU/TPU offloading."""

    def __init__(self, wsl_distro: Optional[str] = None):
        self.wsl_distro = wsl_distro

    def _run_wsl_cmd(self, command: str) -> subprocess.CompletedProcess:
        wsl_args = ["wsl"]
        if self.wsl_distro:
            wsl_args.extend(["-d", self.wsl_distro])
        # Execute using bash login shell ensuring PATH includes ~/.local/bin
        escaped = command.replace('"', '\\"')
        wsl_args.extend(["-e", "bash", "-c", f"export PATH=\"$HOME/.local/bin:$PATH\"; {command}"])
        return subprocess.run(wsl_args, capture_output=True, text=True)

    def check_status(self) -> Dict[str, str]:
        """Check active Colab sessions and CLI availability."""
        res = self._run_wsl_cmd("colab sessions")
        return {
            "returncode": str(res.returncode),
            "stdout": res.stdout,
            "stderr": res.stderr,
        }

    def run_script(self, script_path_on_wsl: str) -> Dict[str, str]:
        """Run a Python script on a fresh Colab VM via `colab run`."""
        res = self._run_wsl_cmd(f"colab run {script_path_on_wsl}")
        return {
            "returncode": str(res.returncode),
            "stdout": res.stdout,
            "stderr": res.stderr,
        }

    def execute_in_session(self, session_id: str, code: str) -> Dict[str, str]:
        """Execute Python code in an existing active Colab session."""
        cmd = f"colab exec {session_id} \"{code}\""
        res = self._run_wsl_cmd(cmd)
        return {
            "returncode": str(res.returncode),
            "stdout": res.stdout,
            "stderr": res.stderr,
        }
