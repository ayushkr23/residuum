"""Local séance server: static UI + optional live generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from residuum import DEFAULT_MODEL_ID, __version__

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
RESULTS = ROOT / "results"

_vessel = None
_vector = None
_meta: dict = {}


class GenerateIn(BaseModel):
    user: str = Field(min_length=1, max_length=500)
    condition: str = "steered"
    coeff: float | None = None
    temperature: float = 0.7
    max_new_tokens: int = 64


def create_app() -> FastAPI:
    app = FastAPI(title="Residuum", version=__version__)

    @app.get("/api/health")
    def health() -> dict:
        replay = RESULTS / "replay.json"
        return {
            "ok": True,
            "version": __version__,
            "live_model_loaded": _vessel is not None,
            "replay_ready": replay.exists(),
            "model_id": _meta.get("model_id"),
        }

    @app.get("/api/replay")
    def replay() -> JSONResponse:
        path = RESULTS / "replay.json"
        if not path.exists():
            web_copy = WEB / "data" / "replay.json"
            path = web_copy if web_copy.exists() else path
        if not path.exists():
            return JSONResponse({"error": "run python -m residuum.experiment first"}, status_code=404)
        return JSONResponse(json.loads(path.read_text(encoding="utf-8")))

    @app.get("/api/facts")
    def facts() -> JSONResponse:
        path = RESULTS / "facts.json"
        if not path.exists():
            path = WEB / "data" / "facts.json"
        if not path.exists():
            return JSONResponse({"error": "facts.json missing"}, status_code=404)
        return JSONResponse(json.loads(path.read_text(encoding="utf-8")))

    @app.post("/api/generate")
    def gen(body: GenerateIn) -> JSONResponse:
        if _vessel is None or _vector is None:
            return JSONResponse(
                {"error": "live model not loaded. Start with: python -m residuum.server --live"},
                status_code=503,
            )
        from residuum.generate import generate, lens_for_prompt
        from residuum.metrics import haunt_rate, is_haunted
        from residuum.prompts import GHOST_SYSTEM, HELPFUL_SYSTEM, EXORCISM_PREFIX

        coeff = body.coeff if body.coeff is not None else float(_meta.get("chosen_coeff", 2.0))
        name = body.condition
        user = body.user
        system = HELPFUL_SYSTEM
        use_vec = False
        if name == "prompt_persona":
            system = GHOST_SYSTEM
        elif name == "steered":
            use_vec = True
        elif name == "prompt_exorcism":
            system = GHOST_SYSTEM
            user = EXORCISM_PREFIX + user
        elif name == "steered_exorcism":
            use_vec = True
            user = EXORCISM_PREFIX + user
        out = generate(
            _vessel,
            user,
            system=system,
            vector=_vector if use_vec else None,
            coeff=coeff if use_vec else 0.0,
            max_new_tokens=body.max_new_tokens,
            temperature=body.temperature,
            seed=0,
        )
        lens = lens_for_prompt(_vessel, user, system=system, top_k=5)
        return JSONResponse(
            {
                "text": out["text"],
                "haunted": is_haunted(out["text"]),
                "haunt_rate": haunt_rate(out["text"]),
                "logit_lens": lens,
                "condition": name,
                "coeff": coeff if use_vec else 0.0,
                "layer": _vector.layer,
            }
        )

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB / "index.html")

    if WEB.exists():
        app.mount("/static", StaticFiles(directory=str(WEB)), name="static")
        data = WEB / "data"
        if data.exists():
            app.mount("/data", StaticFiles(directory=str(data)), name="data")
    return app


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--live", action="store_true", help="load the open-weight model for live possession")
    p.add_argument("--model", default=DEFAULT_MODEL_ID)
    args = p.parse_args(argv)

    if args.live:
        from residuum.extract import extract_vector
        from residuum.model import load_vessel

        global _vessel, _vector, _meta
        facts_path = RESULTS / "facts.json"
        layer = None
        coeff = 2.0
        if facts_path.exists():
            facts = json.loads(facts_path.read_text(encoding="utf-8"))
            layer = int(facts["chosen_layer"])
            coeff = float(facts["chosen_coeff"])
        print("[residuum] loading vessel…")
        _vessel = load_vessel(args.model)
        if layer is None:
            layer = _vessel.n_layers // 2
        print(f"[residuum] extracting vector at layer {layer}")
        _vector = extract_vector(_vessel, layer)
        _meta = {"model_id": _vessel.model_id, "chosen_layer": layer, "chosen_coeff": coeff}

    import uvicorn

    app = create_app()
    print(f"[residuum] http://{args.host}:{args.port}  (replay UI; --live for inference)")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
