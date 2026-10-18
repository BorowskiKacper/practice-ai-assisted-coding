"""Convenience entry point for Arena Player."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("arena_player.main:app", host="0.0.0.0", port=8000, reload=True)

