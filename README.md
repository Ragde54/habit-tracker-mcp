## Tool access policy

The AI has no delete capabilities by design. Destructive operations
(delete habit, delete category, delete todo) are intentionally omitted
from the MCP tool set and reserved for direct database access or a
future frontend interface.

To permanently remove data, connect directly to the database:
sqlite3 habit_tracker.db
