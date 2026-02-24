async def extract_message_context(message, channel) -> dict:
    lines = []

    if channel.type in ("private_thread", "public_thread"):
        async for msg in channel.history(limit=20, oldest_first=True):
            if msg.content.strip():
                lines.append(f"[{msg.author.name}]: {msg.content}")
    else:
        lines.append(f"[{message.author.name}]: {message.content}")

    return {
        "raw": "\n".join(lines),
        "source_url": message.jump_url,
        "channel_name": channel.name,
        "author": message.author.name,
    }