import time


def notify_precheck_start(logger, client, channel_id=None, message="", commit_sha=""):
    logger.info("Sending precheck start notification")
    client.send_message(channel_id=channel_id, message=message)
    client.send_message(channel_id=channel_id, message=".koibotping")
    time.sleep(2)
    messages = client.read_messages(channel_id=channel_id, limit=2)
    for message in messages:
        if message["author"]["username"] == "billbot" and message["content"].startswith(
            "Koibot received"
        ):
            client.send_message(
                channel_id=channel_id,
                message=f"Signing off on `{commit_sha}` for @WiIIiamTang",
            )
            return True
    return False


def save_bot_data(logger, client, channel_id=None):
    logger.info("Saving bot data")
    # TODO: flush cog cache may take a long time and not work very well
    client.send_message(channel_id=channel_id, message=".flush_cog_cache")
    time.sleep(2)
    client.send_message(channel_id=channel_id, message=".force_cog_cache_sync")
    time.sleep(3)
    client.send_message(channel_id=channel_id, message=".force_db_archive_sync")
    time.sleep(3)
    client.send_message(channel_id=channel_id, message=".force_db_sync")
    time.sleep(3)

    messages = client.read_messages(channel_id=channel_id, limit=12)
    done_count = 0
    for message in messages:
        if message["author"]["username"] == "billbot" and message["content"].startswith(
            "Done"
        ):
            done_count += 1

    return done_count >= 3


def notify_precheck_end(logger, client, channel_id=None, message=""):
    logger.info("Sending precheck end notification")
    client.send_message(channel_id=channel_id, message=message)


def check_bot_startup_ready(logger, client, channel_id=None):
    logger.info("Checking bot startup ready")
    client.send_message(
        channel_id=channel_id,
        message="Received bot on alert, starting postcheck tasks:",
    )
    client.send_message(channel_id=channel_id, message=".addpath /app/custom_cogs")
    client.send_message(channel_id=channel_id, message=".load audio")
    time.sleep(1)
    client.send_message(channel_id=channel_id, message=".load alias")
    time.sleep(1)
    client.send_message(channel_id=channel_id, message=".alias global add p play")
    client.send_message(channel_id=channel_id, message=".alias global add join summon")
    client.send_message(channel_id=channel_id, message=".audioset emptydisconnect 10")
    client.send_message(channel_id=channel_id, message=".load custompics")
    time.sleep(16)
    client.send_message(channel_id=channel_id, message=".koibotping")
    time.sleep(1)
    messages = client.read_messages(channel_id=channel_id, limit=4)
    for message in messages:
        if message["author"]["username"] == "billbot" and message["content"].startswith(
            "Koibot received"
        ):
            return True

    return False


def handle_check_bot_startup(logger, client, channel_id=None, retries=3, count=1):
    logger.info(f"Tries: {count}")
    success = check_bot_startup_ready(logger, client, channel_id)
    if count < retries and not success:
        time.sleep(1)
        return handle_check_bot_startup(logger, client, channel_id, retries, count + 1)
    return success
