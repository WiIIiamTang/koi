def notify_precheck_start(logger, client, channel_id, message):
    logger.info("Sending precheck start notification")
    client.send_message(channel_id=channel_id, message=message)


def save_bot_data(logger, client, channel_id):
    logger.info("Saving bot data")
    client.send_message(channel_id=channel_id, message=".flush_cog_cache")
    client.send_message(channel_id=channel_id, message=".force_cog_cache_sync")
    client.send_message(channel_id=channel_id, message=".force_db_archive_sync")
    client.send_message(channel_id=channel_id, message=".force_db_sync")

    messages = client.read_messages(channel_id=channel_id, limit=20)
    for message in messages:
        if message["content"].startswith("Done"):
            return True

    return False


def notify_precheck_end(logger, client, channel_id, message):
    logger.info("Sending precheck end notification")
    client.send_message(channel_id=channel_id, message=message)


def check_bot_startup_ready(logger, client, channel_id):
    logger.info("Checking bot startup ready")
    client.send_message(channel_id=channel_id, message=".koibotping")
    messages = client.read_messages(channel_id=channel_id, limit=4)
    for message in messages:
        if message["content"].startswith("Koibot received"):
            return True

    return False
