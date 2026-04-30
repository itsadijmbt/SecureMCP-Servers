fmt:
	uv run black .
	uv run ruff check . --fix

lint:
	uv run black . --check
	uv run ruff check .

deploy-and-run:
	BUNDLE_VAR_schema_full_name=$(schema_full_name) BUNDLE_VAR_genie_space_ids=$(genie_space_ids) \
		databricks bundle deploy -p $(profile)

	BUNDLE_VAR_schema_full_name=$(schema_full_name) BUNDLE_VAR_genie_space_ids=$(genie_space_ids) \
		databricks bundle run mcp-on-apps -p $(profile)