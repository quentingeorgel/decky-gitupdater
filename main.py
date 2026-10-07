import os
import re
import json
import shutil
import zipfile
import tempfile
import asyncio
import urllib.request
from pathlib import Path

import decky

PLUGINS_DIR = Path(decky.DECKY_PLUGIN_DIR).parent
SETTINGS_DIR = Path(decky.DECKY_PLUGIN_SETTINGS_DIR)
REPOS_FILE = SETTINGS_DIR / "repos.txt"

LINE_RE = re.compile(
    r"^(?P<repo>[\w.-]+/[\w.-]+)"
    r"(?:@(?P<tag>[\w.-]+))?"
    r"(?:#(?P<name>[\w.-]+))?$"
)


def _parse_repos(text: str):
    repos = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = LINE_RE.match(line)
        if not m:
            decky.logger.warning(f"Ligne ignorée (format invalide) : {line}")
            continue
        repos.append({
            "repo": m.group("repo"),
            "tag": m.group("tag"),
            "name": m.group("name"),
            "raw": line,
        })
    return repos


def _resolve_release(repo: str, tag: str | None):
    if tag:
        return tag

    url = f"https://github.com/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "decky-gitupdater"},
        method="HEAD",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        final_url = resp.geturl()

    if "/releases/tag/" not in final_url:
        raise RuntimeError(f"Impossible de résoudre le tag pour {repo}")

    return final_url.rstrip("/").split("/releases/tag/")[-1]


def _find_zip_asset(repo: str, tag: str):
    url = f"https://github.com/{repo}/releases/tag/{tag}"
    req = urllib.request.Request(url, headers={"User-Agent": "decky-gitupdater"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    matches = re.findall(
        r'href="(/' + re.escape(repo) + r'/releases/download/[^"]+\.zip)"',
        html,
    )
    if not matches:
        raise RuntimeError(f"Aucun asset .zip trouvé pour {repo}@{tag}")

    return f"https://github.com{matches[0]}"


def _read_local_version(plugin_name: str):
    manifest = PLUGINS_DIR / plugin_name / "plugin.json"
    if not manifest.exists():
        return None
    try:
        return json.loads(manifest.read_text()).get("version")
    except Exception:
        return None


def _install_zip(zip_path: Path, target_name: str):
    target = PLUGINS_DIR / target_name
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp_path)

        entries = list(tmp_path.iterdir())
        if len(entries) == 1 and entries[0].is_dir():
            source = entries[0]
        else:
            source = tmp_path

        if not (source / "plugin.json").exists():
            raise RuntimeError("Le ZIP ne contient pas de plugin.json à la racine")

        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)


class Plugin:
    async def get_repos(self):
        if not REPOS_FILE.exists():
            return ""
        return REPOS_FILE.read_text()

    async def save_repos(self, text: str):
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        REPOS_FILE.write_text(text)
        return True

    async def check_all(self):
        text = await self.get_repos()
        repos = _parse_repos(text)
        results = []
        for entry in repos:
            name = entry["name"] or entry["repo"].split("/")[-1]
            local = _read_local_version(name)
            try:
                tag = await asyncio.to_thread(
                    _resolve_release, entry["repo"], entry["tag"]
                )
                results.append({
                    "repo": entry["repo"],
                    "name": name,
                    "local": local,
                    "remote": tag,
                    "update_available": local != tag,
                    "error": None,
                })
            except Exception as e:
                decky.logger.error(f"Check échoué {entry['repo']}: {e}")
                results.append({
                    "repo": entry["repo"],
                    "name": name,
                    "local": local,
                    "remote": None,
                    "update_available": False,
                    "error": str(e),
                })
        return results

    async def install(self, repo: str, tag: str, name: str):
        try:
            zip_url = await asyncio.to_thread(_find_zip_asset, repo, tag)
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                req = urllib.request.Request(
                    zip_url, headers={"User-Agent": "decky-gitupdater"}
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    shutil.copyfileobj(resp, tmp)
                tmp_path = Path(tmp.name)
            await asyncio.to_thread(_install_zip, tmp_path, name)
            tmp_path.unlink(missing_ok=True)
            return {"success": True, "installed": tag}
        except Exception as e:
            decky.logger.error(f"Install échouée {repo}@{tag}: {e}")
            return {"success": False, "error": str(e)}

    async def _main(self):
        decky.logger.info("Git Updater démarré")

    async def _unload(self):
        pass
