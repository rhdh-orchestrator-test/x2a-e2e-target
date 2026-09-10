# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains educational examples demonstrating Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec used for compliance testing. Migration complexity is minimal as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains demonstration content that combines Ansible playbooks with Chef InSpec testing:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache web server with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, directory structure creation

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to disable SSLv3 and enforce TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification on Ubuntu 20.04
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocols, and web content
- `tests/ssh_profile.rb`: InSpec security profile testing SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with native Ansible testing modules (ansible.builtin.uri, ansible.builtin.service_facts, community.crypto.openssl_certificate_info)
- **Test Kitchen**: Replace with molecule for Ansible playbook testing
- **Chef Automate/Server**: Remove deployment scripts as they're not needed for pure Ansible infrastructure

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks implement proper SSL hardening (TLS 1.2 enforcement, SSLv3 disabled)
- **Certificate Management**: Self-signed certificates are generated securely using ansible.builtin.openssl_* modules
- **SSH Security**: InSpec tests verify SSH root login restrictions per STIG requirements
- **Credential Management**: No hardcoded credentials detected in playbooks; variables are properly externalized

### Technical Challenges

- **Testing Framework Migration**: Replace InSpec compliance tests with Ansible native testing approaches (testinfra, molecule, or ansible.builtin.assert tasks)
- **Compliance Verification**: Migrate STIG-based security controls from InSpec to Ansible compliance collections (e.g., ansible-security.hardening)
- **Test Kitchen Replacement**: Implement molecule-based testing workflow for playbook validation

### Migration Order

1. **Testing Framework Setup** (low risk, foundational)
   - Replace Test Kitchen with molecule
   - Convert InSpec tests to Ansible native assertions
2. **Playbook Enhancement** (moderate complexity)
   - Add compliance verification tasks directly to playbooks
   - Implement proper error handling and idempotency checks
3. **Documentation Update** (low complexity)
   - Update README files to reflect pure Ansible approach
   - Remove Chef-specific deployment scripts

### Assumptions

- The primary goal is to maintain the educational value while removing Chef InSpec dependency
- Ubuntu 20.04 remains the target platform (though playbooks should be made more OS-agnostic)
- Test Kitchen workflow needs replacement with molecule for consistent testing
- The demonstration scenarios (HTTPS setup, POODLE fix) should remain functionally identical
- InSpec compliance tests represent security requirements that must be preserved in the migrated solution
- The repository serves as educational content rather than production infrastructure code
- No production systems depend on the Chef Automate/Server deployment scripts