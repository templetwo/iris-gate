.PHONY: dialogue-run dialogue-api test-send

dialogue-run:
	python3 scripts/dialogue_loop.py --tick 15

dialogue-api:
	uvicorn services.dialogue_api:app --host 0.0.0.0 --port 8787

test-send:
	@echo "Testing dialogue send..."
	@export PEER_BASE_URL="http://localhost:8787" && \
	export DIALOGUE_AUTH_TOKEN="test-token-12345" && \
	curl -X POST "$$PEER_BASE_URL/inbox" \
		-H "Authorization: Bearer $$DIALOGUE_AUTH_TOKEN" \
		-H "Content-Type: application/json" \
		-d '{"session_id":"TEST","message_id":"'"$$(uuidgen)"'","sender":"test","role":"user","text":"Test message","ts":"'"$$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'"}'
