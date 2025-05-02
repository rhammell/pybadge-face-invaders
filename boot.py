import storage

# Enable writng to local storage
storage.remount("/", disable_concurrent_write_protection=True)
