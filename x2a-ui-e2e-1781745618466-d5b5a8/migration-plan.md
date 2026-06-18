# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef tools
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed, can be used as-is.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible's built-in assert module for basic tests
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Consider integrating with other compliance tools like OSCAP

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Consider alternatives:
  - Option 1: Ansible Tower/AWX for enterprise management
  - Option 2: GitLab CI/CD for pipeline-based automation
  - Option 3: Jenkins with Ansible plugins

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ remains enforced
  - Consider adding more modern security headers
  - Maintain proper certificate handling

- **SSH Security**: The InSpec tests check for SSH root login security. Migration should:
  - Preserve SSH hardening checks
  - Consider expanding to additional SSH security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions and may not have direct equivalents.
  - Mitigation: Consider using a combination of Ansible assert module and custom scripts where needed.

- **Chef Automate Functionality**: If Chef Automate is being used for compliance reporting, finding an equivalent in the Ansible ecosystem may be challenging.
  - Mitigation: Evaluate Ansible Tower/AWX compliance reporting capabilities or integrate with third-party compliance tools.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, requires replacement with Ansible Tower/AWX deployment)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README.md mentioning it's a companion to a white paper.
2. The Chef InSpec tests are used for compliance verification only and not for broader infrastructure testing.
3. The deployment scripts are examples and not used in production environments (they contain hardcoded credentials).
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The migration will maintain the same functionality but using Ansible-native tools where possible.
7. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates.