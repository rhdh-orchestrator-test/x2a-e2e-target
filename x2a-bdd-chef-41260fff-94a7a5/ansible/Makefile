.PHONY: generate_artifacts push_artifacts

ARTIFACT_SUBMISSION_URL ?= http://localhost:8080/artifacts

generate_artifacts:
	@printf '%s\n' '123as artifact' > 123as.txt
	@printf '%s\n' 'c artifact' > c.txt
	@printf '%s\n' 'b artifact' > b.txt

push_artifacts: c.txt
	@curl --fail --show-error --silent --upload-file c.txt "$(ARTIFACT_SUBMISSION_URL)"
