.PHONY: generate_artifacts push_artifacts

ARTIFACT_SUBMISSION_URL ?= http://localhost:8080/artifacts

# Generate the custom artifacts used by the BDD workflow.
generate_artifacts:
	printf '%s\n' '123as' > 123as.txt
	printf '%s\n' 'c' > c.txt
	printf '%s\n' 'b' > b.txt

# Upload c.txt to the configured artifact submission endpoint.
push_artifacts: generate_artifacts
	curl --fail --show-error --silent --upload-file c.txt "$(ARTIFACT_SUBMISSION_URL)"
