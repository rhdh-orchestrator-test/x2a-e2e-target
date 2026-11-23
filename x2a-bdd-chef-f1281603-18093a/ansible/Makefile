.PHONY: generate_artifacts push_artifacts

ARTIFACT_SUBMISSION_URL ?= http://localhost:8080/artifacts

generate_artifacts:
	@printf '123as artifact\n' > 123as.txt
	@printf 'c artifact\n' > c.txt
	@printf 'b artifact\n' > b.txt

push_artifacts: generate_artifacts
	@curl --fail --silent --show-error --upload-file c.txt "$(ARTIFACT_SUBMISSION_URL)"
