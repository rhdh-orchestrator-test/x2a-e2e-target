.PHONY: generate_artifacts push_artifacts

ARTIFACT_SUBMISSION_URL ?= http://localhost:8080/artifacts

generate_artifacts:
	printf '%s\n' '123as' > 123as.txt
	printf '%s\n' 'c' > c.txt
	printf '%s\n' 'b' > b.txt

push_artifacts: generate_artifacts
	curl --fail --upload-file c.txt "$(ARTIFACT_SUBMISSION_URL)"
