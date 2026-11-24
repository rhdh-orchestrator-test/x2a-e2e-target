ARTIFACT_SUBMISSION_URL ?= http://localhost:8080/artifacts

.PHONY: generate_artifacts push_artifacts

generate_artifacts:
	@printf 'generated artifact\n' > 123as.txt
	@printf 'artifact payload\n' > c.txt
	@printf 'build metadata\n' > b.txt

push_artifacts: generate_artifacts
	@curl --fail --show-error --silent --upload-file c.txt "$(ARTIFACT_SUBMISSION_URL)"
