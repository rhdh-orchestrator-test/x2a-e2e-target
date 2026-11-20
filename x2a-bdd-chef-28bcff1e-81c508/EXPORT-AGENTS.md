## FLPATH-4982 BDD Makefile rule

# FLPATH-4982 BDD Makefile rule

During migration, create a functional ansible/Makefile for custom artifacts. It must define generate_artifacts and push_artifacts targets. The generate_artifacts target must create 123as.txt, c.txt, and b.txt. The push_artifacts target must use curl to upload c.txt to the configured artifact submission URL.