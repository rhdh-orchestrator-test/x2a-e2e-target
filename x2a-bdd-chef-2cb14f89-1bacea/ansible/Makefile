.PHONY: generate_artifacts push_artifacts

ARTIFACT_SUBMISSION_URL ?= http://localhost:8080/artifacts

# Generate the BDD custom artifacts expected by the migration workflow.
generate_artifacts:
	@printf '123as artifact\n' > 123as.txt
	@printf 'c artifact\n' > c.txt
	@printf 'b artifact\n' > b.txt

# Upload c.txt to the configured artifact submission endpoint.
push_artifacts: generate_artifacts
	@curl --fail --show-error --silent --upload-file c.txt "$(ARTIFACT_SUBMISSION_URL)"
