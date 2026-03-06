import os
from pathlib import Path
from urllib.parse import urlparse

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from env_loader import load_project_env
from lang import T

load_project_env()
PATH_RESOLUTION_ROOTS = [
    Path.cwd(),
    Path(__file__).resolve().parent.parent,
    Path(__file__).resolve().parent,
]

# === CONFIGURATION ===
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION_STRING")

mode = os.environ.get("MODE", "dev").lower()

client = TelegramClient(StringSession(session_string), api_id, api_hash)

def normalize_channel_ref(channel_ref):
    ref = channel_ref.strip()
    if not ref:
        return ref

    if ref.startswith("http://") or ref.startswith("https://"):
        parsed = urlparse(ref)
        host = parsed.netloc.lower().replace("www.", "")
        if host in {"t.me", "telegram.me"}:
            parts = [part for part in parsed.path.split("/") if part]
            if parts:
                return f"@{parts[0]}"

    return ref


def read_source_channel_refs():
    source_channels_file_raw = os.environ.get("SOURCE_CHANNELS_FILE")
    if not source_channels_file_raw:
        raise ValueError(T["source_file_missing"])

    source_channels_path = Path(source_channels_file_raw)
    if not source_channels_path.is_absolute():
        resolved_path = None
        for base_path in PATH_RESOLUTION_ROOTS:
            candidate = base_path / source_channels_path
            if candidate.is_file():
                resolved_path = candidate
                break
        if resolved_path is None:
            # Keep deterministic path in the error message.
            resolved_path = PATH_RESOLUTION_ROOTS[0] / source_channels_path
        source_channels_path = resolved_path

    if not source_channels_path.is_file():
        raise FileNotFoundError(f"{T['source_file_not_found']} {source_channels_path}")

    refs = []
    with open(source_channels_path, "r", encoding="utf-8") as channels_file:
        for raw_line in channels_file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            refs.append(normalize_channel_ref(line))

    if not refs:
        raise ValueError(f"{T['source_file_empty']} {source_channels_path}")

    return refs


async def resolve_source_channel_ids():
    source_channel_refs = read_source_channel_refs()
    source_channel_ids = []

    print(T["resolving_sources"])
    for channel_ref in source_channel_refs:
        try:
            entity = await client.get_entity(channel_ref)
        except Exception as exc:
            raise ValueError(f"{T['source_not_found']} {channel_ref}") from exc

        source_channel_ids.append(entity.id)
        channel_name = getattr(entity, "title", None) or getattr(entity, "username", "unknown")
        print(f"✅ {T['source_found']} : {channel_name} (ID: {entity.id})")

    return source_channel_ids


async def resolve_target_channel():
    target_channel_id_raw = os.environ.get("TARGET_CHANNEL_ID", "").strip()
    if not target_channel_id_raw:
        raise ValueError(T["target_missing"])

    try:
        target_channel_id = int(target_channel_id_raw)
    except Exception as exc:
        raise ValueError(f"{T['target_invalid_id']} {target_channel_id_raw}") from exc

    try:
        target_entity = await client.get_entity(target_channel_id)
    except Exception as exc:
        raise ValueError(f"{T['target_not_found']} {target_channel_id}") from exc

    target_name = getattr(target_entity, "title", None) or getattr(target_entity, "username", "unknown")
    print(f"✅ {T['target_found']} : {target_name} (ID: {target_channel_id})")
    return target_channel_id


async def main():
    await client.start()

    if mode == "prod":
        print(T["mode_prod"])
    else:
        print(T["mode_dev"])

    source_channel_ids = await resolve_source_channel_ids()
    target_channel_id = await resolve_target_channel()

    @client.on(events.NewMessage(chats=source_channel_ids))
    async def handler(event):
        print(T["new_message"])

        await client.forward_messages(target_channel_id, event.message)
        print(f"{T['forwarded']} {target_channel_id}")

    print(T["listening"])
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
