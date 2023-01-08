import time


def notify_precheck_start(logger, client, channel_id=None, message=""):
    logger.info("Sending precheck start notification")
    client.send_message(channel_id=channel_id, message=message)


def save_bot_data(logger, client, channel_id=None):
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


def notify_precheck_end(logger, client, channel_id=None, message=""):
    logger.info("Sending precheck end notification")
    client.send_message(channel_id=channel_id, message=message)


def check_bot_startup_ready(logger, client, channel_id=None):
    logger.info("Checking bot startup ready")
    client.send_message(channel_id=channel_id, message=".koibotping")
    time.sleep(1)
    messages = client.read_messages(channel_id=channel_id, limit=4)
    for message in messages:
        if message["content"].startswith("Koibot received"):
            return True

    return False


def handle_check_bot_startup(logger, client, channel_id=None, retries=3, count=1):
    logger.info(f"Tries: {count}")
    success = check_bot_startup_ready(logger, client, channel_id)
    if count < retries and not success:
        time.sleep(1)
        return handle_check_bot_startup(logger, client, channel_id, retries, count + 1)
    return success
