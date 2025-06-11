import storage

# Enable writing to local storage
storage.remount("/", disable_concurrent_write_protection=True)
